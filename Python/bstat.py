#!/usr/bin/env python
import sys
import serial
import time
from config_parser import cfg
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient

method = cfg.modbus.method
baudrate = cfg.modbus.baudr
parity = cfg.modbus.parity
port = cfg.modbus.portname
timeout = cfg.modbus.timeout

# Connecting to boiler via modbus protocol


def get_boiler_stats():
    boiler_stats = [0, 0, 0, 0, 0, 0]
    try:
        modbus_client = ModbusSerialClient(method=method,
                                           baudrate=baudrate,
                                           parity=parity,
                                           port=port,
                                           timeout=timeout)
        modbus_client.connect()
    except (ModbusException, OSError) as e:
        return boiler_stats

    c_to_f = lambda t: round(((9.0 / 5.0) * t + 32.0), 1)
    for i in range(3):
        try:
            # Read one register from 40006 address to get System Supply Temperature
            # Memory map for the boiler is here on page 8:
            # http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf
            hregs = modbus_client.read_holding_registers(6, count=1, unit=1)
            # Read 9 registers from 30003 address
            iregs = modbus_client.read_input_registers(3, count=9, unit=1)
            boiler_stats = [c_to_f(hregs.getRegister(0) / 10.0),
                            c_to_f(iregs.getRegister(5) / 10.0),
                            c_to_f(iregs.getRegister(6) / 10.0),
                            c_to_f(iregs.getRegister(7) / 10.0),
                            float(iregs.getRegister(3)),
                            float(iregs.getRegister(8))]
        except (OSError, serial.SerialException, ModbusException, AttributeError, IndexError) as e:
            time.sleep(0.7)
        else:
            break
    modbus_client.close()
    return boiler_stats

if __name__ == '__main__':
    print(";".join(["{0:.1f}".format(v) for v in get_boiler_stats()]))
