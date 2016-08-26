import os
import sys
import json
import serial
import urllib2

class Struct(object):

    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

config_path = "/etc/chronos_config.json"

with open(config_path) as config:
    cfg = json.load(config, object_hook=Struct)

def relay_read(relay_number):
    with serial.Serial(cfg.serial.portname,
                       cfg.serial.baudr,
                       timeout=1) as ser_port:
        ser_port.write("relay read {}\n\r".format(relay_number))
        response = ser_port.read(25)
        if response.find("on") > 0:
                return "Relay {} is ON".format(relay_number)
        elif response.find("off") > 0:
                return "Relay {} is OFF".format(relay_number)

def get_data_from_web():
    content = urllib2.urlopen(
        "http://wx.thomaslivestock.com/downld02.txt"
    )
    last_line = content.readlines()[-1].split()
    wind_chill = float(last_line[12])
    temp_out = float(last_line[2])
    return wind_chill, temp_out

def read_temperature_sensor(sensor_id):
    device_file = os.path.join(
        "/sys/bus/w1/devices", sensor_id, "w1_slave"
    )
    while True:
        try:
            with open(device_file) as content:
                lines = content.readlines()
        except IOError as e:
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

def main():
    water_out_temp = read_temperature_sensor(cfg.sensors.out_id)
    return_temp = read_temperature_sensor(cfg.sensors.in_id)
    wind_chill, temp_out = get_data_from_web()
    for device, relay_number in cfg.relay.__dict__.items():
        print("{}. {}".format(device, relay_read(relay_number)))
    print("Water out temp: {}".format(water_out_temp))
    print("Return temp: {}".format(return_temp))
    print("Wind Chill: {}".format(wind_chill))
    print("Temp Out: {}".format(temp_out))

if __name__ == '__main__':
    main()