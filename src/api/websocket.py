"""WebSocket support for real-time market data streaming."""
import asyncio, json, logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info("WebSocket connected to channel: %s", channel)

    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        """Remove a WebSocket connection."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        """Broadcast a message to all connections in a channel."""
        if channel not in self.active_connections:
            return
        dead = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                dead.add(connection)
        self.active_connections[channel] -= dead

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a single connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    @property
    def total_connections(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())

manager = ConnectionManager()
