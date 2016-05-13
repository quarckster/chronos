#!/usr/bin/env python

import sys
import signal
from datetime import datetime
from chronos.lib import Chronos
from SimpleWebSocketServer import SimpleWebSocketServer
from chronos.lib.websocket_server import WebSocketServer
from chronos.lib.root_logger import root_logger as logger

chronos = Chronos()
websocket_server = SimpleWebSocketServer("0.0.0.0", 8000, WebSocketServer)


def destructor(signum=None, frame=None, status=0):
    chronos.scheduler.shutdown(wait=False)
    websocket_server.close()
    chronos.turn_off_devices(relay_only=True)
    sys.exit(status)

signal.signal(signal.SIGTERM, destructor)


def main():
    logger.info("Starting chronos")
    chronos.initialize_state()
    chronos.scheduler.add_job(
        websocket_server.serveforever,
        "date",
        run_date=datetime.now()
    )
    chronos.scheduler.add_job(chronos.update_history, "cron", minute="*")
    chronos.scheduler.add_job(chronos.get_data_from_web, "cron", minute="*")
    chronos.scheduler.start()
    try:
        while True:
            chronos_mode = chronos.mode
            if chronos_mode == 0:
                chronos.boiler.send_stats()
                if chronos.boiler.manual_override != 2:
                    chronos.boiler.set_boiler_setpoint(
                        chronos.effective_setpoint
                    )
                    chronos.boiler_switcher()
                if chronos.is_time_to_switch_season_on_summer:
                    chronos.switch_season("to_summer")
            elif chronos_mode == 1:
                chronos.chillers_cascade_switcher()
                if chronos.is_time_to_switch_season_on_winter:
                    chronos.switch_season("to_winter")
    except KeyboardInterrupt:
        destructor()
    except Exception as e:
        logger.exception(e)
        destructor(status=1)

if __name__ == "__main__":
    main()
