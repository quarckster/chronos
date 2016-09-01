import os
import sys
import time
import serial
import urllib2
from chronos.lib import db
from collections import OrderedDict
from chronos.lib.config_parser import cfg


def relay_read(relay_number):
    with serial.Serial(cfg.serial.portname, cfg.serial.baudr, timeout=1) as ser_port:
        ser_port.write("relay read {}\n\r".format(relay_number))
        response = ser_port.read(25)
    if "on" in response:
        state = "ON"
    elif "off" in response:
        state = "OFF"
    return state


def get_data_from_web():
    content = urllib2.urlopen("http://wx.thomaslivestock.com/downld02.txt")
    last_line = content.readlines()[-1].split()
    wind_chill = float(last_line[12])
    temp_out = float(last_line[2])
    return wind_chill, temp_out


def read_temperature_sensor(sensor_id):
    device_file = os.path.join("/sys/bus/w1/devices", sensor_id, "w1_slave")
    while True:
        try:
            with open(device_file) as content:
                lines = content.readlines()
        except IOError:
            sys.exit("Couldn't read data from sensors")
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


def get_settings():
    with db.session_scope() as session:
        result = session.query(db.Settings).first()
        settings = {
            "Mode change delta temp": result.mode_change_delta_temp,
            "Setpoint max": result.setpoint_max,
            "Setpoint min": result.setpoint_min,
            "Cascade time": result.cascade_time,
            "Setpoint offset winter": result.setpoint_offset_winter,
            "Setpoint offset summer": result.setpoint_offset_summer,
            "Tolerance": result.tolerance,
            "Mode": result.mode
        }
    return settings


def main():
    water_out_temp = read_temperature_sensor(cfg.sensors.out_id)
    return_temp = read_temperature_sensor(cfg.sensors.in_id)
    wind_chill, temp_out = get_data_from_web()
    relays_dict = {device: [relay_read(relay_number), relay_number] for device, relay_number in
                   cfg.relay.__dict__.items()}
    sorted_relays_dict = OrderedDict(sorted(relays_dict.items(), key=lambda t: t[0]))
    for device,(relay_state, relay_number) in sorted_relays_dict.items():
        print("{}: {}; relay number: {}".format(device, relay_state, relay_number))
    for param, value in get_settings().items():
        print("{}: {}".format(param, value))
    print("Water out temp: {}".format(water_out_temp))
    print("Return temp: {}".format(return_temp))
    print("Wind Chill: {}".format(wind_chill))
    print("Temp Out: {}".format(temp_out))

if __name__ == '__main__':
    main()
