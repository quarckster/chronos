import sys
from root_logger import root_logger
from config_parser import cfg
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient

# Connecting to boiler via modbus protocol
try:
    modbus_client = ModbusSerialClient(method=cfg.modbus.method,
                                 	   baudrate=cfg.modbus.baudr,
                                       parity=cfg.modbus.parity,
                                       port=cfg.modbus.portname,
                                       timeout=cfg.modbus.timeout)
    modbus_client.connect()
except (ModbusException, OSError) as e:
    root_logger.exception("Cannot connect to the boiler via modbus: %s" % e)