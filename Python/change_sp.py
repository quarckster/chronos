#!/usr/bin/env python
import logging
import sys
import time
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = ModbusClient(method="rtu",
                      baudrate=9600,
                      parity="E",
                      port="/dev/ttyUSB0",
                      timeout=0.5)
client.connect()
while True:
    try:
        rr = client.read_holding_registers(0, 7, unit=1)
        print(dir(rr))
        print("Reg40001: {}".format(rr.getRegister(0)));
        print("Reg40002: {}".format(rr.getRegister(1)));
        print("Reg40003: {}".format(rr.getRegister(2)));
        print("Reg40004: {}".format(rr.getRegister(3)));
        print("Reg40005: {}".format(rr.getRegister(4)));
        print("Reg40006: {}".format(rr.getRegister(5)));
    except (AttributeError, IndexError):
        time.sleep(1)
    else:
        break

setpoint = int(-101.4856 + 1.7363171*int(sys.argv[1]))

assert(setpoint > 0 and setpoint < 100)

client.write_register(0, 4, unit=1)

client.write_register(2, setpoint, unit=1)

client.close()