import os
import sys
import time
import serial
import urllib2
from chronos.lib import db
from sqlalchemy import desc
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from chronos.lib import websocket_client
from chronos.lib.config_parser import cfg
from pymodbus.exceptions import ModbusException
from chronos.lib.modbus_client import modbus_session
from chronos.lib.root_logger import root_logger as logger
from apscheduler.schedulers.background import BackgroundScheduler


def timer():
    for i in reversed(xrange(120)):
        websocket_client.send_message({"timer": i})
        time.sleep(1)


class Device(object):

    def _switch_state(self, command, relay_only=False):
        try:
            with serial.Serial(
                cfg.serial.portname,
                cfg.serial.baudr,
                timeout=1
            ) as ser_port:
                ser_port.write("relay {} {}\n\r".format(
                    command, self.relay_number
                ))
        except serial.SerialException as e:
            logger.exception("Serial port error: {}".format(e))
            sys.exit(1)
        else:
            logger.debug("Relay {} has been turned {}. Relay only: {}".format(
                self.relay_number, command, relay_only
            ))
            if command == "on" and not relay_only:
                self._update_value_in_db("status", 1)
            elif command == "off" and not relay_only:
                self._update_value_in_db("status", 0)

    def turn_on(self, relay_only=False):
        self._switch_state("on", relay_only=relay_only)

    def turn_off(self, relay_only=False):
        self._switch_state("off", relay_only=relay_only)

    def _get_property_from_db(self, from_backup=False):
        device = getattr(db, self.device)
        with db.session_scope() as session:
            property_ = session.query(device).filter(
                device.backup == from_backup
            ).first()
            session.expunge(property_)
        return property_

    def _update_value_in_db(self, name, value, to_backup=False):
        device = getattr(db, self.device)
        with db.session_scope() as session:
            property_ = session.query(device).filter(
                device.backup == to_backup
            ).first()
            setattr(property_, name, value)
        logger.debug("Db has been updated. {} {}: {}. Backup: {}".format(
            self.device, name, value, to_backup
        ))
        if not to_backup and name != "switched_timestamp":
            if name == "timestamp":
                value = value.strftime("%B %d, %I:%M %p")
            websocket_client.send_message({
                "device": self.number,
                name: value
            })

    def save_status(self):
        self._update_value_in_db("status", self.status, to_backup=True)
        self._update_value_in_db(
            "manual_override", self.manual_override, to_backup=True
        )
        self._update_value_in_db(
            "switched_timestamp", self.switched_timestamp, to_backup=True
        )

    def restore_status(self):
        status = self._get_property_from_db(from_backup=True).status
        manual_override = self._get_property_from_db(
            from_backup=True).manual_override
        switched_timestamp = self._get_property_from_db(
            from_backup=True).switched_timestamp
        self._update_value_in_db("status", status)
        self._update_value_in_db("manual_override", manual_override)
        self._update_value_in_db("switched_timestamp", switched_timestamp)

    @property
    def status(self):
        return self._get_property_from_db().status

    @property
    def manual_override(self):
        return self._get_property_from_db().manual_override

    @manual_override.setter
    def manual_override(self, manual_override):
        if manual_override == 1:
            if self.status != 1:
                self.turn_on()
            self._update_value_in_db("manual_override", 1)
        elif manual_override == 2:
            if self.status != 0:
                self.turn_off()
            self._update_value_in_db("manual_override", 2)
        elif manual_override == 0:
            self._update_value_in_db("manual_override", 0)


class Chiller(Device):

    def __init__(self, number):
        if number not in range(1, 5):
            raise ValueError("Chiller number must be in range from 1 to 4")
        else:
            self.number = number
            self.relay_number = getattr(cfg.relay, "chiller{}".format(number))
            self.device = "Chiller{}".format(number)

    @property
    def timestamp(self):
        return self._get_property_from_db().timestamp

    @property
    def switched_timestamp(self):
        return self._get_property_from_db().switched_timestamp

    def turn_off(self, relay_only=False):
        super(Chiller, self).turn_off(relay_only=relay_only)
        if not relay_only:
            self._update_value_in_db("switched_timestamp", datetime.now())

    def turn_on(self, relay_only=False):
        super(Chiller, self).turn_on(relay_only=relay_only)
        if not relay_only:
            now = datetime.now()
            self._update_value_in_db("timestamp", now)
            self._update_value_in_db("switched_timestamp", now)


class Boiler(Device):

    def __init__(self):
        self.number = 0
        self.relay_number = cfg.relay.boiler
        self.device = "Boiler"

    @property
    def timestamp(self):
        return self._get_property_from_db().timestamp

    @property
    def switched_timestamp(self):
        return self._get_property_from_db().switched_timestamp

    @property
    def cascade_current_power(self):
        return self._get_property_from_db().cascade_current_power

    @property
    def lead_firing_rate(self):
        return self._get_property_from_db().lead_firing_rate

    def set_boiler_setpoint(self, effective_setpoint):
        setpoint = int(-101.4856 + 1.7363171 * int(effective_setpoint))
        if not (setpoint > 0 and setpoint < 100):
            for i in range(3):
                try:
                    with modbus_session() as modbus:
                        modbus.write_register(0, 4, unit=cfg.modbus.unit)
                        modbus.write_register(
                            2, setpoint, unit=cfg.modbus.unit)
                except (ModbusException, serial.SerialException, OSError):
                    logger.exception("Modbus error")
                    time.sleep(0.5)
                else:
                    logger.info(
                        "Setpoint {} has been sent to boiler".format(setpoint)
                    )
                    break

    def send_stats(self):
        def c_to_f(t):
            return round(((9.0 / 5.0) * t + 32.0), 1)
        boiler_stats = {
            "system_supply_temp": 0,
            "outlet_temp": 0,
            "inlet_temp": 0,
            "flue_temp": 0,
            "cascade_current_power": 0,
            "lead_firing_rate": 0
        }
        for i in range(1, 4):
            try:
                with modbus_session() as modbus:
                    # Read one register from 40006 address
                    # to get System Supply Temperature
                    # Memory map for the boiler is here on page 8:
                    # http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf
                    hregs = modbus.read_holding_registers(
                        6, count=1, unit=cfg.modbus.unit
                    )
                    # Read 9 registers from 30003 address
                    iregs = modbus.read_input_registers(
                        3, count=9, unit=cfg.modbus.unit
                    )
                    boiler_stats = {
                        "system_supply_temp": c_to_f(
                            hregs.getRegister(0) / 10.0),
                        "outlet_temp": c_to_f(iregs.getRegister(5) / 10.0),
                        "inlet_temp": c_to_f(iregs.getRegister(6) / 10.0),
                        "flue_temp": c_to_f(iregs.getRegister(7) / 10.0),
                        "cascade_current_power": float(iregs.getRegister(3)),
                        "lead_firing_rate": float(iregs.getRegister(8))
                    }
            except (AttributeError, IndexError):
                logger.exception("Attempt {}. Modbus answer is empty, "
                                 "retrying.".format(i))
                time.sleep(1)
            except (OSError, ModbusException, serial.SerialException):
                logger.exception("Cannot to connect to modbus")
                break
            else:
                logger.info("Attempt {}. {}".format(i, boiler_stats))
                break
        for key, value in boiler_stats.items():
            self._update_value_in_db(key, value)
            websocket_client.send_message({key: value})


class Valve(Device):

    def __init__(self, number):
        if number not in (1, 2):
            raise ValueError("Valve number must be in range from 1 to 2")
        else:
            self.number = number
            self.relay_number = getattr(cfg.relay, "valve{}".format(number))
            self.device = "Valve{}".format(number)

    def __getattr__(self, name):
        if name in ("status", "timestamp", "save_status", "restore_status"):
            raise AttributeError("There is no such atrribute")
        super(Valve, self).__getattr__(name)

    def turn_on(self):
        super(Valve, self).turn_on(relay_only=True)

    def turn_off(self):
        super(Valve, self).turn_off(relay_only=True)


class Chronos(object):

    def __init__(self):
        self.boiler = Boiler()
        self.chiller1 = Chiller(1)
        self.chiller2 = Chiller(2)
        self.chiller3 = Chiller(3)
        self.chiller4 = Chiller(4)
        self.valve1 = Valve(1)
        self.valve2 = Valve(2)
        self.devices = (
            self.boiler,
            self.chiller1,
            self.chiller2,
            self.chiller3,
            self.chiller4
        )
        self._outside_temp = None
        self._wind_speed = None
        self.data = {}
        self.scheduler = BackgroundScheduler()

    def _read_temperature_sensor(self, sensor_id):
        device_file = os.path.join(
            "/sys/bus/w1/devices", sensor_id, "w1_slave"
        )
        while True:
            try:
                with open(device_file) as content:
                    lines = content.readlines()
            except IOError as e:
                logger.exception("Temp sensor error: {}".format(e))
                sys.exit(1)
            else:
                if lines[0].strip()[-3:] == "YES":
                    break
                else:
                    time.sleep(0.2)
        equals_pos = lines[1].find("t=")
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            # Divide by 1000 for proper decimal point
            temp = float(temp_string) / 1000.0
            # Convert to degF
            temp = temp * 9.0 / 5.0 + 32.0
            # Round temp to 2 decimal points
            temp = round(temp, 1)
            return temp

    @property
    def water_out_temp(self):
        water_out_temp = self._read_temperature_sensor(cfg.sensors.out_id)
        websocket_client.send_message({"water_out_temp": water_out_temp})
        self.data["water_out_temp"] = water_out_temp
        return water_out_temp

    @property
    def return_temp(self):
        return_temp = self._read_temperature_sensor(cfg.sensors.in_id)
        websocket_client.send_message({"return_temp": return_temp})
        self.data["return_temp"] = return_temp
        return return_temp

    def get_data_from_web(self):
        logger.debug("Retrieve data from web.")
        try:
            content = urllib2.urlopen(
                "http://wx.thomaslivestock.com/downld02.txt"
            )
        except (IOError, urllib2.HTTPError, urllib2.URLError):
            logger.exception("""Unable to get data from website.
                                Reading previous value from DB.""")
            with db.session_scope() as session:
                wind_speed, outside_temp = session.query(
                    db.History.wind_speed, db.History.outside_temp
                ).order_by(desc(db.History.id)).first()
        else:
            last_line = content.readlines()[-1].split()
            wind_speed = float(last_line[7])
            # Wind chill
            if self.mode in (0, 2):
                outside_temp = float(last_line[12])
            # Temperature
            elif self.mode in (1, 3):
                outside_temp = float(last_line[2])
        self._outside_temp = outside_temp
        self._wind_speed = wind_speed
        self.data["outside_temp"] = outside_temp
        websocket_client.send_message({"outside_temp": outside_temp})
        return {
            "outside_temp": outside_temp,
            "wind_speed": wind_speed
        }

    @property
    def outside_temp(self):
        return self._outside_temp or self.get_data_from_web()["outside_temp"]

    @property
    def wind_speed(self):
        return self._wind_speed or self.get_data_from_web()["wind_speed"]

    def _get_settings_from_db(self):
        with db.session_scope() as session:
            property_ = session.query(db.Settings).first()
            session.expunge(property_)
        return property_

    def _update_settings(self, name, value):
        with db.session_scope() as session:
            property_ = session.query(db.Settings).first()
            setattr(property_, name, value)
        if name == "cascade_time":
            value /= 60
        websocket_client.send_message({name: value})

    @property
    def setpoint_offset_summer(self):
        return self._get_settings_from_db().setpoint_offset_summer

    @setpoint_offset_summer.setter
    def setpoint_offset_summer(self, setpoint_offset):
        self._update_settings("setpoint_offset_summer", setpoint_offset)

    @property
    def setpoint_offset_winter(self):
        return self._get_settings_from_db().setpoint_offset_winter

    @setpoint_offset_winter.setter
    def setpoint_offset_winter(self, setpoint_offset):
        self._update_settings("setpoint_offset_winter", setpoint_offset)

    @property
    def mode(self):
        mode = self._get_settings_from_db().mode
        self.data["mode"] = mode
        return mode

    @mode.setter
    def mode(self, mode):
        self._update_settings("mode", mode)

    @property
    def setpoint_min(self):
        return self._get_settings_from_db().setpoint_min

    @setpoint_min.setter
    def setpoint_min(self, setpoint):
        self._update_settings("setpoint_min", setpoint)

    @property
    def setpoint_max(self):
        return self._get_settings_from_db().setpoint_max

    @setpoint_max.setter
    def setpoint_max(self, setpoint):
        self._update_settings("setpoint_max", setpoint)

    @property
    def tolerance(self):
        return self._get_settings_from_db().tolerance

    @tolerance.setter
    def tolerance(self, tolerance):
        self._update_settings("tolerance", tolerance)

    @property
    def cascade_time(self):
        return self._get_settings_from_db().cascade_time / 60

    @cascade_time.setter
    def cascade_time(self, cascade_time):
        self._update_settings("cascade_time", cascade_time * 60)

    @property
    def mode_change_delta_temp(self):
        return self._get_settings_from_db().mode_change_delta_temp

    @mode_change_delta_temp.setter
    def mode_change_delta_temp(self, mode_change_delta_temp):
        self._update_settings("mode_change_delta_temp", mode_change_delta_temp)

    def get_wind_chill_avg(self, mode=None):
        mode = mode or self.mode
        mode_map = {0: 0, 1: 1, 2: 0, 3: 1, "winter": 0, "summer": 1}
        with db.session_scope() as session:
            wind_chill_avg = session.query(
                func.avg(db.History.outside_temp)).filter(
                db.History.mode == mode_map[mode],
                db.History.timestamp > (datetime.now() - timedelta(days=4))
            ).first()[0]
        wind_chill_avg = wind_chill_avg or self.outside_temp
        return int(round(wind_chill_avg))

    @property
    def wind_chill_avg(self):
        return self.get_wind_chill_avg()

    @property
    def cascade_fire_rate_avg(self):
        timespan = datetime.now() - timedelta(hours=cfg.efficiency.hours)
        with db.session_scope() as session:
            average_cascade_fire_rate = session.query(
                func.avg(db.History.cascade_fire_rate)
            ).order_by(desc(db.History.id)).filter(
                db.History.mode == 0,
                db.History.timestamp > timespan
            ).first()[0]
        return average_cascade_fire_rate or 0

    @property
    def baseline_setpoint(self):
        wind_chill = int(round(self.outside_temp))
        if wind_chill < 11:
            baseline_setpoint = 100
        else:
            with db.session_scope() as session:
                baseline_setpoint = session.query(
                    db.SetpointLookup.setpoint
                ).filter(db.SetpointLookup.wind_chill == wind_chill).first()[0]
        websocket_client.send_message({"baseline_setpoint": baseline_setpoint})
        return baseline_setpoint

    def get_tha_setpoint(self, mode=None):
        if self.get_wind_chill_avg(mode) < 71:
            temperature_history_adjsutment = 0
        else:
            with db.session_scope() as session:
                temperature_history_adjsutment = session.query(
                    db.SetpointLookup.setpoint_offset
                ).filter(db.SetpointLookup.avg_wind_chill ==
                         self.wind_chill_avg).first()[0]
        tha_setpoint = self.baseline_setpoint - temperature_history_adjsutment
        websocket_client.send_message({"tha_setpoint": tha_setpoint})
        return tha_setpoint

    @property
    def tha_setpoint(self):
        return self.get_tha_setpoint()

    @property
    def effective_setpoint(self):
        "Calculate setpoint from wind_chill."
        if self.mode in (0, 2):
            effective_setpoint = (self.tha_setpoint +
                                  self.setpoint_offset_winter)
        elif self.mode in (1, 3):
            effective_setpoint = (self.tha_setpoint +
                                  self.setpoint_offset_summer)
        # constrain effective setpoint
        if effective_setpoint > self.setpoint_max:
            effective_setpoint = self.setpoint_max
        elif effective_setpoint < self.setpoint_min:
            effective_setpoint = self.setpoint_min
        websocket_client.send_message({
            "effective_setpoint": effective_setpoint
        })
        self.data["effective_setpoint"] = effective_setpoint
        return effective_setpoint

    def boiler_switcher(self):
        logger.debug("Starting boiler switcher")
        if self.boiler.manual_override == 0:
            if ((self.boiler.status == 0 and
                 self.return_temp) <= (self.effective_setpoint -
                                       self.tolerance)):
                self.boiler.turn_on()
            elif ((self.boiler.status == 1 and
                   self.return_temp) > (self.effective_setpoint +
                                        self.tolerance)):
                self.boiler.turn_off()
        logger.debug("Boiler: {}; mode: {}".format(
            self.boiler.status, self.mode))

    def _find_chiller_index_to_switch(self, status):
        min_date = datetime.now()
        switch_index = None
        for i, chiller in enumerate(self.devices[1:], 1):
            if (chiller.timestamp < min_date and
                    chiller.manual_override == 0 and
                    chiller.status == status):
                min_date = chiller.timestamp
                switch_index = i
        return switch_index

    @property
    def previous_return_temp(self):
        with db.session_scope() as session:
            previous_return_temp = session.query(
                db.History.return_temp
            ).order_by(desc(db.History.id)).first()[0]
        return float(previous_return_temp)

    @property
    def current_delta(self):
        current_delta = self.return_temp - self.previous_return_temp
        if current_delta > 0.2:
            current_delta = 1
        elif current_delta < 0:
            current_delta = -1
        else:
            current_delta = 0
        self.data["current_delta"] = current_delta
        return current_delta

    @property
    def _max_chillers_timestamp(self):
        max_timestamp = datetime.min
        for chiller in self.devices[1:]:
            if chiller.switched_timestamp > max_timestamp:
                max_timestamp = chiller.switched_timestamp
        return max_timestamp

    def chillers_cascade_switcher(self):
        logger.debug("Chiller cascade switcher")
        time_gap = (datetime.now() -
                    self._max_chillers_timestamp).total_seconds()
        turn_off_index = self._find_chiller_index_to_switch(1)
        turn_on_index = self._find_chiller_index_to_switch(0)
        logger.debug("; ".join(
            "{}: {}".format(k, v) for k, v in self.data.items())
        )
        logger.debug(
            "time_gap: {}; turn_on_index: {}; turn_off_index: {}".format(
                time_gap, turn_on_index, turn_off_index
            )
        )
        # Turn on chillers
        if (self.return_temp >= (self.effective_setpoint +
                                 self.tolerance) and
                self.current_delta == 1 and
                time_gap >= self.cascade_time * 60 and
                turn_on_index is not None):
            self.devices[turn_on_index].turn_on()
        # Turn off chillers
        elif (self.return_temp < (self.effective_setpoint -
                                  self.tolerance) and
                self.current_delta in (-1, 0) and
                time_gap >= self.cascade_time * 60 and
                turn_off_index is not None):
            self.devices[turn_off_index].turn_off()

    def initialize_state(self):
        for device in self.devices:
            if device.manual_override == 1:
                device.turn_on(relay_only=True)
            elif device.manual_override == 2:
                device.turn_off(relay_only=True)
            elif device.manual_override == 0:
                if device.status == 1:
                    device.turn_on(relay_only=True)
                elif device.status == 0:
                    device.turn_off(relay_only=True)

    def turn_off_devices(self, relay_only=False):
        if relay_only:
            for device in self.devices:
                device.turn_off(relay_only=relay_only)
        else:
            for device in self.devices:
                device.manual_override = 2

    def update_history(self):
        logger.debug("Updating history")
        mode = self.mode
        if mode in (0, 1):
            with db.session_scope() as session:
                parameters = db.History(
                    outside_temp=self.outside_temp,
                    effective_setpoint=self.effective_setpoint,
                    water_out_temp=self.water_out_temp,
                    return_temp=self.return_temp,
                    boiler_status=self.boiler.status,
                    cascade_fire_rate=self.boiler.cascade_current_power,
                    lead_fire_rate=self.boiler.lead_firing_rate,
                    chiller1_status=self.chiller1.status,
                    chiller2_status=self.chiller2.status,
                    chiller3_status=self.chiller3.status,
                    chiller4_status=self.chiller4.status,
                    tha_setpoint=self.tha_setpoint,
                    setpoint_offset_winter=self.setpoint_offset_winter,
                    setpoint_offset_summer=self.setpoint_offset_summer,
                    tolerance=self.tolerance,
                    boiler_manual_override=self.boiler.manual_override,
                    chiller1_manual_override=self.chiller1.manual_override,
                    chiller2_manual_override=self.chiller2.manual_override,
                    chiller3_manual_override=self.chiller3.manual_override,
                    chiller4_manual_override=self.chiller4.manual_override,
                    mode=mode,
                    cascade_time=self.cascade_time,
                    wind_speed=self.wind_speed,
                    avg_outside_temp=self.wind_chill_avg,
                    avg_cascade_fire_rate=self.cascade_fire_rate_avg,
                    delta=self.current_delta
                )
                session.add(parameters)

    def switch_season(self, mode):
        if mode == "to_summer":
            logger.debug("Switching to summer mode")
            self.mode = 3
            self._save_devices_states(mode)
            self.turn_off_devices()
            self.valve1.turn_on()
            self.valve2.turn_off()
            self.scheduler.add_job(
                self.switch_season,
                "date",
                run_date=datetime.now() + timedelta(minutes=2),
                args=["from_winter"]
            )
            self.scheduler.add_job(
                timer,
                "date",
                run_date=datetime.now()
            )
        elif mode == "to_winter":
            logger.debug("Switching to winter mode")
            self.mode = 2
            self._save_devices_states(mode)
            self.turn_off_devices()
            self.valve1.turn_off()
            self.valve2.turn_on()
            self.scheduler.add_job(
                self.switch_season,
                "date",
                run_date=datetime.now() + timedelta(minutes=2),
                args=["from_summer"]
            )
            self.scheduler.add_job(
                timer,
                "date",
                run_date=datetime.now()
            )
        elif mode == "from_summer":
            logger.debug("Switched to winter mode")
            self._restore_devices_states(mode)
            self.initialize_state()
            self.mode = 0
        elif mode == "from_winter":
            logger.debug("Switched to summer mode")
            self._restore_devices_states(mode)
            self.initialize_state()
            self.mode = 1

    def _save_devices_states(self, mode):
        if mode == "to_summer":
            self.boiler.save_status()
        elif mode == "to_winter":
            for chiller in self.devices[1:]:
                chiller.save_status()

    def _restore_devices_states(self, mode):
        if mode == "from_summer":
            self.boiler.restore_status()
        elif mode == "from_winter":
            for chiller in self.devices[1:]:
                chiller.restore_status()

    @property
    def is_time_to_switch_season_to_summer(self):
        effective_setpoint = (self.get_tha_setpoint("winter") +
                              self.setpoint_offset_winter)
        # constrain effective setpoint
        if effective_setpoint > self.setpoint_max:
            effective_setpoint = self.setpoint_max
        elif effective_setpoint < self.setpoint_min:
            effective_setpoint = self.setpoint_min
        return (self.return_temp > (effective_setpoint +
                                    self.mode_change_delta_temp))

    @property
    def is_time_to_switch_season_to_winter(self):
        effective_setpoint = (self.get_tha_setpoint("summer") +
                              self.setpoint_offset_summer)
        # constrain effective setpoint
        if effective_setpoint > self.setpoint_max:
            effective_setpoint = self.setpoint_max
        elif effective_setpoint < self.setpoint_min:
            effective_setpoint = self.setpoint_min
        return (self.return_temp < (effective_setpoint -
                                    self.mode_change_delta_temp))
