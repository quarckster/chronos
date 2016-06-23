import json
import time
import websocket
from chronos.lib.root_logger import root_logger as logger

websocket_client = None


def send_message(data):
    global websocket_client
    if websocket_client is None:
        websocket_client = websocket.WebSocket()
        websocket_client.connect("ws://127.0.0.1:8000/")
    for i in range(1, 4):
        try:
            websocket_client.send(unicode(json.dumps(data)))
        except Exception:
            time.sleep(1)
            logger.exception("Reconnecting to websocket server")
            websocket_client = websocket.WebSocket()
            websocket_client.connect("ws://127.0.0.1:8000/")
            websocket_client.send(unicode(json.dumps(data)))