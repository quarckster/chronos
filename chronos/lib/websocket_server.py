import json
from SimpleWebSocketServer import WebSocket
from chronos.lib.root_logger import root_logger as logger

websocket_clients = []


class WebSocketServer(WebSocket):

    def handleConnected(self):
        logger.debug("{}:{} connected".format(
            self.address[0], self.address[1])
        )
        websocket_clients.append(self)

    def handleClose(self):
        logger.debug(websocket_clients)
        try:
            websocket_clients.remove(self)
        except ValueError as e:
            logger.debug("{}, {}".format(self, e))
        else:
            pass
        logger.debug("{}:{} closed".format(
            self.address[0], self.address[1])
        )

    def handleMessage(self):
        for client in websocket_clients:
            if client != self and client.address != "127.0.0.1":
                client.sendMessage(self.data)


def send_message(data):
    data = unicode(json.dumps(data))
    if websocket_clients:
        for client in websocket_clients:
            client.sendMessage(data)
