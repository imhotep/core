"""Unifi Access Door Module."""
from collections.abc import Callable
import logging

_LOGGER = logging.getLogger(__name__)


class UnifiAccessDoor:
    """Unifi Access Door Class."""

    def __init__(
        self,
        door_id: str,
        name: str,
        door_position_status: str,
        door_lock_relay_status: str,
        hub,
    ) -> None:
        """Initialize door."""
        self._callbacks: set[Callable] = set()
        self._is_locking = False
        self._is_unlocking = False
        self._hub = hub
        self._id = door_id
        self.name = name
        self.door_position_status = door_position_status
        self.door_lock_relay_status = door_lock_relay_status
        self.doorbell_pressed = False
        self.doorbell_request_id = None

    @property
    def id(self) -> str:
        """Get door ID."""
        return self._id

    @property
    def is_open(self):
        """Get door status."""
        return self.door_position_status == "open"

    @property
    def is_locked(self):
        """Solely used for locked state when calling lock."""
        return self.door_lock_relay_status == "lock"

    @property
    def is_locking(self):
        """Solely used for locking state when calling lock."""
        return False

    @property
    def is_unlocking(self):
        """Solely used for unlocking state when calling unlock."""
        return self._is_unlocking

    def unlock(self) -> None:
        """Unlock door."""
        if self.is_locked:
            self._is_unlocking = True
            self._hub.unlock_door(self._id)
            self._is_unlocking = False
            _LOGGER.info("Door with door ID %s is unlocked", self.id)
        else:
            _LOGGER.error("Door with door ID %s is already unlocked", self.id)

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()
