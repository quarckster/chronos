#!/usr/bin/env python

import time
import os
import urllib2
import subprocess
import signal
import sys
import serial
from lxml import etree
from root_logger import root_logger
from config_parser import cfg
from modbus_client import modbus_client, ModbusException
from db_conn import conn, MySQLdb_error

# Constants
DEVICE_DIR = cfg.files.sys_devices_dir
SYSTEMUP = cfg.files.systemup_path
FIRMWARE_UPGRADE = cfg.files.firmware_upgrade
# Set relay numbers
boiler_pin = cfg.relay.boiler
chiller_pin = [0]*4
chiller_pin[0] = cfg.relay.chiller1
chiller_pin[1] = cfg.relay.chiller2
chiller_pin[2] = cfg.relay.chiller3
chiller_pin[3] = cfg.relay.chiller4
valve1_pin = cfg.relay.valve1
valve2_pin = cfg.relay.valve2
led_red = cfg.relay.led_red
led_green = cfg.relay.led_green
led_blue = cfg.relay.led_blue
# Temp sensors
sensor_out_id = cfg.sensors.out_id 
sensor_in_id = cfg.sensors.in_id

def update_systemUp():
    try:
        with open(SYSTEMUP, "w") as dataFile:
            dataFile.write("ONLINE\n")
    except IOError as e:
        root_logger.exception("Can't write to systemUp.txt: %s" % e)


def switch_relay(number, command):
    if command in [1, True]:
        command = "on"
    elif command in [0, False]:
        command = "off"
    # Check availability of the serial port
    try:
        with serial.Serial(cfg.serial.portname,
                           cfg.serial.baudr,
                           timeout=1) as ser_port:
            ser_port.write("relay %s %s\n\r" % (command, number))
    except serial.SerialException as e:
        root_logger.exception("Serial port error: %s" % e)
        sys.exit(1)


def manage_system(power_mode):
    "Check for shutdown, restart, etc."
    if power_mode == 10:
        subprocess.call(["reboot"])
    elif power_mode == 20:
        subprocess.call(["shutdown", "now"])
    elif power_mode == 2:
        subprocess.call(["python", FIRMWARE_UPGRADE])
        time.sleep(10)
    elif power_mode == 7:
        subprocess.call(["python",
                         "/home/pi/Desktop/Chronos/Chronos_starter.py"])
        time.sleep(10)


def check_mysql():
    "Check if MySQL service is running."
    error_DB = 0
    try:
        with open("/var/run/mysqld/mysqld.pid") as pid_file:
            pid = int(pid_file.readline())
    except IOError as e:
        error_DB = 1
        root_logger.exception("Can't read mysql pid file: %s" % e)
    else:
        try:
            os.kill(pid, 0)
        except OSError:
            error_DB = 1
            root_logger.exception("MySQL is not running")
            destructor()
    return error_DB


def read_temp(device_file):
    while True:
        with open(device_file) as content:
            lines = content.readlines()
        if lines[0].strip()[-3:] == "YES":
            break
        else:
            time.sleep(0.2)
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        # Divide by 1000 for proper decimal point
        temp = float(temp_string) / 1000.0
        # Convert to degF
        temp = temp * 9.0 / 5.0 + 32.0
        # Round temp to 2 decimal points
        temp = round(temp, 1)
        return temp


def read_temperature_sensors():
    "Read Temperature Sensors."
    error_T1 = 1
    error_T2 = 1
    water_out_temp = 00.00
    for directory in os.listdir(DEVICE_DIR):
        if directory in (sensor_in_id, sensor_out_id):
            device_folder = os.path.join(DEVICE_DIR, directory)
            device_file = os.path.join(device_folder, "w1_slave")
            device_file_ID = os.path.join(device_folder, "name")
            device_id = ""
            try:
                with open(device_file_ID) as content:
                    device_id = content.read(15)
            except IOError as e:
                pass
            try:
                with open(device_file) as content:
                    temp_raw = content.readlines()
            except IOError as e:
                root_logger.exception("Temp sensor error: %s" % e)
                try:
                    with conn:
                        cur = conn.cursor()
                        sql = """SELECT returnTemp
                                 FROM mainTable
                                 ORDER BY LID
                                 DESC LIMIT 1"""
                        cur.execute(sql)
                        results = cur.fetchone()
                    return_temp = results[0]
                except MySQLdb_error:
                    return_temp = 00.00
            if device_id == sensor_out_id:
                water_out_temp = read_temp(device_file)
                error_T2 = 0
            elif device_id == sensor_in_id:
                return_temp = read_temp(device_file)
                error_T1 = 0
    return {"water_out_temp": water_out_temp,
            "return_temp": return_temp,
            "errors": [error_T1, error_T2]}


def blink_leds(water_out_temp, breather_count):
    temp_thresh = 80.00  # Threshold for breather LED color selection
    if water_out_temp > temp_thresh:
        led_breather = led_red
    else:
        led_breather = led_blue
    if breather_count == 0:
        switch_relay(led_breather, "on")
        time.sleep(0.1)
        switch_relay(led_breather, "off")
        time.sleep(0.1)
        switch_relay(led_breather, "on")
        time.sleep(0.1)
        switch_relay(led_breather, "off")
        time.sleep(0.1)
        breather_count += 1
    else:
        breather_count = 0
    return breather_count


def read_values_from_db():
    "Read values from DB."
    try:
        with conn:
            cur = conn.cursor()
            sql1 = """SELECT setPoint2, parameterX, t1, mode, CCT
                      FROM mainTable ORDER BY LID DESC LIMIT 1"""
            cur.execute(sql1)
            result1 = cur.fetchone()
            setpoint2 = result1[0]
            parameterX = result1[1]
            t1 = result1[2]
            mode = result1[3]
            CCT = result1[4]
            sql2 = "SELECT status, MO, timeStamp FROM actStream"
            cur.execute(sql2)
            result2 = cur.fetchall()
            boiler_status = result2[0][0]
            chiller_status = [result2[1][0], result2[2][0], result2[3][0], result2[4][0]]
            MO_B = result2[0][1]
            MO_C = [result2[1][1], result2[2][1], result2[3][1], result2[4][1]]
            time_stamps = [result2[1][2], result2[2][2], result2[3][2], result2[4][2]]
            # power_mode = result[19]
    except MySQLdb_error as e:
        # ON = 1, OFF = 0
        boiler_status = 0
        chiller_status = [0]*4
        setpoint2 = 00.00
        parameterX = 0
        t1 = 0
        # Manual overrides. AUTO = 0, ON = 1, OFF = 2
        MO_B = 0
        MO_C = [0]*4
        # Winter/Summer mode selector (0 -> Winter, 1 -> Summer)
        # Also we need some intermediate modes when valve is switching
        # Let mode will be 2 when summer to winter switching
        # and mode will be 3 when winter to summer
        mode = 0
        power_mode = 0
        CCT = 5  # Chiller Cascade Time
        root_logger.exception("Error fetching data from DB: %s" % e)
    return {"boiler_status": boiler_status,
            "chiller_status": chiller_status,
            "time_stamps": time_stamps,
            "setpoint2": setpoint2,
            "parameterX": parameterX,
            "t1": t1,
            "MO_B": MO_B,
            "MO_C": MO_C,
            "mode": mode,
            # "power_mode": power_mode,
            "CCT": CCT*60}


def get_data_from_web(mode):
    "Parsing windChill and windSpeed from wx.thomaslivestock.com."
    error_Web = 0
    try:
        content = urllib2.urlopen('http://wx.thomaslivestock.com')
    except (IOError, urllib2.HTTPError, urllib2.URLError):
        root_logger.exception("""Unable to get data from website.
                              Reading previous value from DB.""")
        error_Web = 1
        try:
            with conn:
                cur = conn.cursor()
                sql = """SELECT outsideTemp, windSpeed
                         FROM mainTable
                         ORDER BY LID
                         DESC LIMIT 1"""
                cur.execute(sql)
                results = cur.fetchone()
                outside_temp = results[0]
                wind_speed = results[1]
        except MySQLdb_error:
            root_logger.exception("""Unable to get value from DB.
                                 Reverting to default value of 65 deg F""")
            outside_temp = 65.00
            wind_speed = 0.00
    else:
        html = content.read()
        tree = etree.HTML(html)
        # Wind chill
        if mode in (0, 2):
            node = tree.xpath(
                "/html/body/table/tr[10]/td[2]/font/strong/font/small/text()")
        # Temperature
        elif mode in (1, 3):
            node = tree.xpath(
                "/html/body/table/tr[3]/td[2]/font/strong/small/font/text()")
        outTemp = node[0].split(u"\xb0F")[0]
        outside_temp = float(outTemp)
        # Wind speed
        node = tree.xpath(
            "/html/body/table/tr[6]/td[2]/font/strong/font/small/text()")
        wind_speed = float(node[0].split()[2])
    return {"outside_temp": outside_temp,
            "windSpeed": wind_speed,
            "error_Web": error_Web}


def calculate_setpoint(outside_temp, setpoint2, parameterX, mode):
    "Calculate setpoint from windChill."
    wind_chill = int(round(outside_temp))
    try:
        with conn:
            cur = conn.cursor()
            # It needs for correct calculation setpoint when
            # valve is switching
            mode_map = {0: 0, 1: 1, 2: 0, 3: 1}
            sql = ("""SELECT AVG(outsideTemp)
                      FROM mainTable
                      WHERE logdatetime > DATE_SUB(CURDATE(), INTERVAL 96 HOUR)
                      AND mode = %s
                      ORDER BY LID DESC
                      LIMIT 5760""" % mode_map[mode])
            cur.execute(sql)
            result = cur.fetchone()
            if result[0]:
                wind_chill_avg = int(round(result[0]))
            else:
                wind_chill_avg = wind_chill
    except MySQLdb_error as e:
        wind_chill_avg = 0
        root_logger.exception("Unable to get value from DB: %s" % e)
    if wind_chill < 11:
         baseline_setpoint = 100
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPoint
                          FROM SetpointLookup
                          WHERE windChill = %s""" % wind_chill)
                cur.execute(sql)
                results = cur.fetchone()
                baseline_setpoint = results[0]
        except MySQLdb_error as e:
            root_logger.exception("Setpoint error: %s" % e)
    if wind_chill_avg < 71:
        temperature_history_adjsutment = 0
    else:
        try:
            with conn:
                cur = conn.cursor()
                sql = ("""SELECT setPointOffset
                          FROM SetpointLookup
                          WHERE avgWindChill = %s""" % wind_chill_avg)
                cur.execute(sql)
                results = cur.fetchone()
                temperature_history_adjsutment = results[0]
        except MySQLdb_error as e:
            temperature_history_adjsutment = 0
            root_logger.exception("Setpoint error: %s" % e)
    tha_setpoint = baseline_setpoint - temperature_history_adjsutment
    effective_setpoint = tha_setpoint + parameterX
    # constrain effective setpoint
    try:
        with conn:
            cur = conn.cursor()
            sql = "SELECT spMin FROM setpoints"
            cur.execute(sql)
            results = cur.fetchone()
            sp_min =  results[0]
    except MySQLdb_error as e:
        sp_min = 40.00
        root_logger.exception("Unable to read spMin: %s" % e)
    try:
        with conn:
            cur = conn.cursor()
            sql = "SELECT spMax FROM setpoints"
            cur.execute(sql)
            results = cur.fetchone()
            sp_max =  results[0]
    except MySQLdb_error as e:
        sp_max = 100.00
        root_logger.exception("Unable to read spMax: %s" % e)
    if effective_setpoint > sp_max:
        effective_setpoint = sp_max
    elif effective_setpoint < sp_min:
        effective_setpoint = sp_min
    try:
        with conn:
            cur = conn.cursor()
            sql = "UPDATE setpoints SET sp=%s" % effective_setpoint
            cur.execute(sql)
    except MySQLdb_error as e:
        root_logger.exception("Unable to update sp: %s" % e)
    return {"effective_setpoint": effective_setpoint,
            "tha_setpoint": tha_setpoint,
            "wind_chill_avg": wind_chill_avg}


def boiler_switcher(MO_B, mode, return_temp, effective_setpoint, t1, boiler_status):
    new_boiler_status = boiler_status
    if mode in (2, 3):
        new_boiler_status = 0
        switch_relay(boiler_pin, "off")
        # when the user switches between summer/winter modes,
        # all five devices are switched to the manual "off" state
        # and stay off until the user turns them back to "on" or "auto".
        update_actStream_table(new_boiler_status, None, True, MO=2)
    elif MO_B == 0:
        if (new_boiler_status == 0
                and mode == 0
                and return_temp <= (effective_setpoint - t1)):
            new_boiler_status = 1
            switch_relay(boiler_pin, "on")
            update_actStream_table(new_boiler_status, None, True)
        elif (new_boiler_status == 1
                and mode == 0
                and return_temp > (effective_setpoint + t1)):
            new_boiler_status = 0
            switch_relay(boiler_pin, "off")
            update_actStream_table(new_boiler_status, None, True)
    elif MO_B == 1 and new_boiler_status == 0:
        new_boiler_status = 1
        switch_relay(boiler_pin, "on")
        update_actStream_table(new_boiler_status, None, True)
    elif MO_B == 2 and new_boiler_status == 1:
        new_boiler_status = 0
        switch_relay(boiler_pin, "off")
        update_actStream_table(new_boiler_status, None, True)
    root_logger.debug("Boiler: %s; mode: %s" % (new_boiler_status, mode))
    return new_boiler_status

def find_chiller_index_to_switch(time_stamps, MO_C, chiller_status, status):
    min_date = time.time()
    switch_index = None
    for i, (time_stamp, MO_C_item, c_status) in enumerate(zip(time_stamps, MO_C, chiller_status)):
        time_stamp = time.mktime(time_stamp.timetuple())
        if (time_stamp < min_date and MO_C_item == 0 and c_status == status):
            min_date = time_stamp
            switch_index = i
    return switch_index

def chillers_cascade_switcher(effective_setpoint, time_stamps, chiller_status,
                              return_temp, t1, MO_C, CCT, mode):
    time_gap = time.time() - time.mktime(max(time_stamps).timetuple())
    new_chiller_status = chiller_status[:]
    turn_off_index = find_chiller_index_to_switch(time_stamps, MO_C, chiller_status, 1)
    turn_on_index = find_chiller_index_to_switch(time_stamps, MO_C, chiller_status, 0)
    # Turn on chillers
    if (return_temp >= (effective_setpoint + t1)
            and time_gap >= CCT
            and mode == 1
            and turn_on_index is not None):
        new_chiller_status[turn_on_index] = 1
        switch_relay(chiller_pin[turn_on_index], "on")
        update_actStream_table(1, turn_on_index)
    # Turn off chillers
    elif (return_temp < (effective_setpoint - t1)
            and time_gap >= CCT
            and mode == 1
            and turn_off_index is not None):
        new_chiller_status[turn_off_index] = 0
        switch_relay(chiller_pin[turn_off_index], "off")
        update_actStream_table(0, turn_off_index)
    # Turn off chillers when winter or valve is switching
    elif mode in (2, 3) and turn_off_index is not None:
        new_chiller_status[turn_off_index] = 0
        switch_relay(chiller_pin[turn_off_index], "off")
        # when the user switches between summer/winter modes,
        # all five devices are switched to the manual "off" state
        # and stay off until the user turns them back to "on" or "auto".
        update_actStream_table(0, turn_off_index, MO=2)
    string = ", ".join([str(i) for i in new_chiller_status])
    root_logger.debug("Chillers: %s; time gap: %d; mode: %s" % (string, time_gap, mode))
    return new_chiller_status


def switch_valve(mode, valveStatus):
    if mode == 0 and valveStatus != mode:
        switch_relay(valve1_pin, "on")
        switch_relay(valve2_pin, "off")
    elif mode == 1 and valveStatus != mode:
        switch_relay(valve1_pin, "off")
        switch_relay(valve2_pin, "on")
    valveStatus = mode
    return valveStatus


def change_sp(setpoint):
    setpoint = int(-101.4856 + 1.7363171*int(setpoint))
    for i in range(3):
        try:
            assert(setpoint > 0 and setpoint < 100)
            modbus_client.write_register(0, 4, unit=cfg.modbus.unit)
            modbus_client.write_register(2, setpoint, unit=cfg.modbus.unit)
        except (AssertionError, ModbusException, serial.SerialException) as e:
            root_logger.exception(e)
            time.sleep(0.5)
        else:
            break


def update_db(MO, outside_temp, water_out_temp, return_temp, boiler_status,
              chiller_status, setpoint2, wind_speed, avgOutsideTemp):
    try:
        with conn:
            cur = conn.cursor()
            args = [outside_temp, water_out_temp, return_temp, boiler_status, chiller_status[0],
                    chiller_status[1], chiller_status[2], chiller_status[3], setpoint2]
            string1 = ",".join(["\"%s\"" % i for i in args])
            string2 = ",".join(["\"%s\"" % i for i in MO])
            sql2 = ("""INSERT INTO mainTable (logdatetime,
                                              outsideTemp,
                                              waterOutTemp,
                                              returnTemp,
                                              boilerStatus,
                                              chiller1Status,
                                              chiller2Status,
                                              chiller3Status,
                                              chiller4Status,
                                              setPoint2,
                                              parameterX,
                                              t1,
                                              MO_B,
                                              MO_C1,
                                              MO_C2,
                                              MO_C3,
                                              MO_C4,
                                              mode,
                                              powerMode,
                                              CCT,
                                              windSpeed,
                                              avgOutsideTemp)
                       SELECT NOW(),%s,parameterX,t1,%s,mode,powerMode,CCT,\"%s\",\"%s\"
                       FROM mainTable
                       ORDER BY LID DESC
                       LIMIT 1""" % (string1,
                                     string2,
                                     wind_speed,
                                     avgOutsideTemp))
            cur.execute(sql2)
    except MySQLdb_error as e:
        root_logger.exception("Error updating table: %s" % e)


def update_actStream_table(status, chiller_id, boiler=False, MO=False):
    if boiler:
        tid = 1
    else:
        tid = chiller_id + 2
    try:
        with conn:
            cur = conn.cursor()
            if MO:
                sql = ("""UPDATE actStream
                          SET timeStamp=NOW(),
                              status=%s,
                              MO=%s
                          WHERE TID=%s""" % (status, tid, MO))
            else:
                sql = ("""UPDATE actStream
                          SET timeStamp=NOW(),
                              status=%s
                          WHERE TID=%s""" % (status, tid))
            cur.execute(sql)
    except MySQLdb_error as e:
        root_logger.exception("Error updating actStream table: %s" % e)


def update_sysStatus(error_sensor, error_DB, error_Web):
    errData = [error_sensor[0], error_sensor[1], error_DB, error_Web]
    try:
        with open("/var/www/sysStatus.txt", "w") as dataFile:
            for item in errData:
                dataFile.write("%s\n" % str(item))
    except IOError as e:
        root_logger.exception("Error opening file to write: %s" % e)
    try:
        with conn:
            cur = conn.cursor()
            sql = ("""UPDATE errTable
                      SET err_T1=%s,
                          err_T2=%s,
                          err_Web=%s""" % (error_sensor[0],
                                           error_sensor[1],
                                           error_Web))
            cur.execute(sql)
    except MySQLdb_error as e:
        root_logger.exception("Error updating actStream table: %s" % e)            


def destructor(signum=None, frame=None):
    # close db connection
    if conn:
        conn.rollback()
    # close modbus connection
    modbus_client.close()
    # turn off all relays
    for i in vars(cfg.relay).values():
        switch_relay(i, "off")
    with open(SYSTEMUP, "w") as dataFile:
        dataFile.write("OFFLINE\n")
        root_logger.info("Chronos_main shutted down")
    sys.exit(0)

signal.signal(signal.SIGTERM, destructor)

def initialize_chronos_state():
    relays = [cfg.relay.boiler,
              cfg.relay.chiller1,
              cfg.relay.chiller2,
              cfg.relay.chiller3,
              cfg.relay.chiller4]
    db_data = read_values_from_db()
    relays_statuses = []
    relays_statuses.append(db_data["boiler_status"])
    relays_statuses.extend(db_data["chiller_status"])
    relays_mo_statuses = []
    relays_mo_statuses.append(db_data["MO_B"])
    relays_mo_statuses.extend(db_data["MO_C"])
    for relay, relay_status, relay_mo_status in zip(relays,
                                                    relays_statuses,
                                                    relays_mo_statuses):
        if relay_mo_status == 1:
            switch_relay(relay, "on")
        elif relay_mo_status == 2:
            switch_relay(relay, "off")
        elif relay_mo_status == 0:
            switch_relay(relay, relay_status)

if __name__ == "__main__":
    root_logger.info("Starting script")
    breather_count = 0
    valveStatus = 0
    timer = 0 
    update_systemUp()
    initialize_chronos_state()
    try:
        while True:
            error_DB = check_mysql()
            sensors_data = read_temperature_sensors()
            # breather_count = blink_leds(sensors_data["water_out_temp"],
                                        # breather_count)
            db_data = read_values_from_db()
            web_data = get_data_from_web(db_data["mode"])
            setpoint = calculate_setpoint(web_data["outside_temp"],
                                          db_data["setpoint2"],
                                          db_data["parameterX"],
                                          db_data["mode"])
            change_sp(setpoint["effective_setpoint"])
            boiler_status = boiler_switcher(db_data["MO_B"],
                                            db_data["mode"],
                                            sensors_data["return_temp"],
                                            setpoint["effective_setpoint"],
                                            db_data["t1"],
                                            db_data["boiler_status"])
            chiller_status = chillers_cascade_switcher(setpoint["effective_setpoint"],
                                                       db_data["time_stamps"],
                                                       db_data["chiller_status"],
                                                       sensors_data["return_temp"],
                                                       db_data["t1"],
                                                       db_data["MO_C"],
                                                       db_data["CCT"],
                                                       db_data["mode"])
            valveStatus = switch_valve(db_data["mode"], valveStatus)
            # Update db every minute
            if time.time() - timer >= 60:
                MO = []
                MO.append(db_data["MO_B"])
                MO.extend(db_data["MO_C"])
                update_db(MO,
                          web_data["outside_temp"],
                          sensors_data["water_out_temp"],
                          sensors_data["return_temp"],
                          boiler_status,
                          chiller_status,
                          setpoint["tha_setpoint"],
                          web_data["windSpeed"],
                          setpoint["wind_chill_avg"])
                timer = time.time()
            update_sysStatus(sensors_data["errors"],
                             error_DB,
                             web_data["error_Web"])
            # manage_system(db_data["power_mode"])
    except KeyboardInterrupt:
        destructor()
    except Exception as e:
        root_logger.exception(e)