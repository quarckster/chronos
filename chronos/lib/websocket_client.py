import json
import websocket

websocket_client = None


def send_message(data):
    global websocket_client
    if websocket_client is None:
        websocket_client = websocket.WebSocket()
        websocket_client.connect("ws://127.0.0.1:8000/")
    websocket_client.send(unicode(json.dumps(data)))
