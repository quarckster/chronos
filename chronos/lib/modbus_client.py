import time
import serial
from root_logger import root_logger
from config_parser import cfg
from pymodbus.exceptions import ModbusException
from pymodbus.client.sync import ModbusSerialClient

# Connecting to boiler via modbus protocol
class Modbus():

    client = None

    def __init__(self):
        try:
            self.client = ModbusSerialClient(method=cfg.modbus.method,
                                             baudrate=cfg.modbus.baudr,
                                             parity=cfg.modbus.parity,
                                             port=cfg.modbus.portname,
                                             timeout=cfg.modbus.timeout)
            self.client.connect()
        except (ModbusException, OSError) as e:
            root_logger.exception("Unable connect to the boiler via modbus: %s" % e)


def change_sp(setpoint):
    setpoint = int(-101.4856 + 1.7363171*int(setpoint))
    for i in range(3):
        try:
            assert(setpoint > 0 and setpoint < 100)
            modbus = Modbus()
            modbus.client.write_register(0, 4, unit=cfg.modbus.unit)
            modbus.client.write_register(2, setpoint, unit=cfg.modbus.unit)
        except (AssertionError, ModbusException, serial.SerialException) as e:
            root_logger.exception(e)
            time.sleep(0.5)
        else:
            root_logger.info("Setpoint %s has been sent to boiler" % setpoint)
            break
        finally:
            modbus.client.close()


def get_boiler_stats():
    c_to_f = lambda t: round(((9.0/5.0)*t + 32.0), 1)
    boiler_stats = {"system_supply_temp": 0,
                    "outlet_temp": 0,
                    "inlet_temp": 0,
                    "flue_temp": 0,
                    "cascade_current_power": 0,
                    "lead_firing_rate": 0,
                    "error": True}
    for i in range(3):
        try:
            modbus = Modbus()
            # Read one register from 40006 address to get System Supply Temperature
            # Memory map for the boiler is here on page 8:
            # http://www.lochinvar.com/_linefiles/SYNC-MODB%20REV%20H.pdf
            hregs = modbus.client.read_holding_registers(6, count=1, unit=cfg.modbus.unit)
            # Read 9 registers from 30003 address
            iregs = modbus.client.read_input_registers(3, count=9, unit=cfg.modbus.unit)
            boiler_stats = {"system_supply_temp": c_to_f(hregs.getRegister(0)/10.0),
                            "outlet_temp": c_to_f(iregs.getRegister(5)/10.0),
                            "inlet_temp": c_to_f(iregs.getRegister(6)/10.0),
                            "flue_temp": c_to_f(iregs.getRegister(7)/10.0),
                            "cascade_current_power": float(iregs.getRegister(3)),
                            "lead_firing_rate": float(iregs.getRegister(8))}
        except (AttributeError, IndexError):
            root_logger.exception("Attempt {}. Modbus answer is empty, retrying.".format(i+1))
            time.sleep(1)
        except (ModbusException, serial.SerialException, OSError) as e:
            root_logger.exception("Modbus error: %s" % e)
            break
        else:
            boiler_stats["error"] = False
            root_logger.info("Attempt {}. {}".format(i+1, boiler_stats))
            break
        finally:
            modbus.client.close()
    return boiler_stats