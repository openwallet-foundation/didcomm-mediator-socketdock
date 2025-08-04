"""HTTP backend for SocketDock."""

import logging
from typing import Dict, Union

import aiohttp

from .backend import Backend


LOGGER = logging.getLogger(__name__)


class HTTPBackend(Backend):
    """HTTP backend for SocketDock."""

    def __init__(
        self,
        socket_base_uri: str,
        connect_uri: str,
        message_uri: str,
        disconnect_uri: str,
    ):
        """Initialize HTTP backend."""
        self._connect_uri = connect_uri
        self._message_uri = message_uri
        self._disconnect_uri = disconnect_uri
        self.socket_base_uri = socket_base_uri

    def send_callback(self, connection_id: str) -> str:
        """Return the callback URI for sending a message to a connected socket."""
        return f"{self.socket_base_uri}/socket/{connection_id}/send"

    def disconnect_callback(self, connection_id: str) -> str:
        """Return the callback URI for disconnecting a connected socket."""
        return f"{self.socket_base_uri}/socket/{connection_id}/disconnect"

    def callback_uris(self, connection_id: str) -> Dict[str, str]:
        """Return labelled callback URIs."""
        return {
            "send": self.send_callback(connection_id),
            "disconnect": self.disconnect_callback(connection_id),
        }

    async def socket_connected(
        self,
        connection_id: str,
        headers: Dict[str, str],
    ):
        """Handle inbound socket message, with calback provided."""
        http_body = {
            "meta": {
                **self.callback_uris(connection_id),
                "headers": headers,
                "connection_id": connection_id,
            },
        }

        if self._connect_uri:
            async with aiohttp.ClientSession() as session:
                LOGGER.info("Posting message %s to %s", http_body, self._connect_uri)
                async with session.post(self._connect_uri, json=http_body) as resp:
                    response = await resp.text()
                    if resp.status != 200:
                        LOGGER.error("Error posting message: %s", response)
                    else:
                        LOGGER.debug("Response: %s", response)

    async def inbound_socket_message(
        self,
        connection_id: str,
        message: Union[str, bytes],
    ):
        """Handle inbound socket message, with calback provided."""
        http_body = {
            "meta": {
                **self.callback_uris(connection_id),
                "connection_id": connection_id,
            },
            "message": message.decode("utf-8") if isinstance(message, bytes) else message,
        }

        async with aiohttp.ClientSession() as session:
            LOGGER.info("Posting message %s to %s", http_body, self._message_uri)
            async with session.post(self._message_uri, json=http_body) as resp:
                response = await resp.text()
                if resp.status != 200:
                    LOGGER.error("Error posting message: %s", response)
                else:
                    LOGGER.debug("Response: %s", response)

    async def socket_disconnected(self, connection_id: str):
        """Handle socket disconnected."""
        async with aiohttp.ClientSession() as session:
            LOGGER.info(
                "Notifying of disconnect: %s %s", self._disconnect_uri, connection_id
            )
            async with session.post(
                self._disconnect_uri, json={"connection_id": connection_id}
            ) as resp:
                response = await resp.text()
                if resp.status != 200:
                    LOGGER.error("Error posting to disconnect uri: %s", response)
                else:
                    LOGGER.debug("Response: %s", response)
