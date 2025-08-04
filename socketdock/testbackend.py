"""Test backend for SocketDock."""

import logging
from typing import Dict, Union
import aiohttp

from .backend import Backend

LOGGER = logging.getLogger(__name__)


class TestBackend(Backend):
    """Test backend for SocketDock."""

    def __init__(self, base_uri: str):
        """Initialize backend."""
        self.base_uri = base_uri

    async def socket_connected(
        self,
        connection_id: str,
        headers: Dict[str, str],
    ):
        """Socket connected.

        This test backend doesn't care, but can be useful to clean up state.
        """
        LOGGER.debug("Connected to test backend: %s", connection_id)

    async def inbound_socket_message(
        self,
        connection_id: str,
        message: Union[str, bytes],
    ):
        """Receive socket message."""
        LOGGER.debug("Recieved message [%s]: %s", connection_id, message)
        send_uri = f"{self.base_uri}/socket/{connection_id}/send"
        async with aiohttp.ClientSession() as session:
            async with session.post(send_uri, data="Hello yourself") as resp:
                if not resp.ok:
                    raise Exception(f"Failed to post to: {send_uri}")
                response = await resp.text()
                LOGGER.debug("Response: %s", response)

    async def socket_disconnected(self, connection_id: str):
        """Socket disconnected.

        This test backend doesn't care, but can be useful to clean up state.
        """
        LOGGER.debug("Disconnected from test backend: %s", connection_id)
