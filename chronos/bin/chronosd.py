#!/usr/bin/env python

import sys
import signal
from datetime import datetime
from SimpleWebSocketServer import SimpleWebSocketServer
from chronos.lib.websocket_server import WebSocketServer
from chronos.lib.root_logger import root_logger as logger
from chronos.lib import Chronos, WINTER, SUMMER, TO_WINTER, TO_SUMMER, ON, MANUAL_OFF

chronos = Chronos()
websocket_server = SimpleWebSocketServer("0.0.0.0", 8000, WebSocketServer)


def destructor(signum=None, frame=None, status=0):
    websocket_server.close()
    chronos.scheduler.shutdown(wait=False)
    chronos.turn_off_devices(relay_only=True)
    sys.exit(status)


signal.signal(signal.SIGTERM, destructor)


def main():
    logger.info("Starting chronos")
    chronos.initialize_state(with_valves=True)
    chronos.scheduler.add_job(websocket_server.serveforever, "date", run_date=datetime.now())
    chronos.scheduler.add_job(chronos.update_history, "cron", minute="*")
    chronos.scheduler.add_job(chronos.get_data_from_web, "cron", minute="*")
    chronos.scheduler.add_job(chronos.emergency_shutdown, "cron", minute="*/2")
    chronos.scheduler.start()
    try:
        while True:
            mode = chronos.mode
            if mode == WINTER:
                if chronos.boiler.status == ON:
                    chronos.boiler.read_modbus_data()
                if chronos.boiler.manual_override != MANUAL_OFF:
                    chronos.boiler.set_boiler_setpoint(chronos.effective_setpoint)
                    chronos.boiler_switcher()
                if chronos.is_time_to_switch_season_to_summer:
                    chronos.switch_season(TO_SUMMER)
            elif mode == SUMMER:
                chronos.chillers_cascade_switcher()
                if chronos.is_time_to_switch_season_to_winter:
                    chronos.switch_season(TO_WINTER)
    except KeyboardInterrupt:
        destructor()
    except Exception as e:
        logger.exception(e)
        destructor(status=1)


if __name__ == "__main__":
    main()
