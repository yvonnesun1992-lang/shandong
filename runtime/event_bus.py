from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Event:
    type: str
    payload: dict
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC).replace(microsecond=0))


class EventBus:
    VALID_TYPES = {
        "MARKET_TICK",
        "SIGNAL_GENERATED",
        "ORDER_PLACED",
        "ORDER_FILLED",
        "POSITION_UPDATED",
        "RISK_TRIGGERED",
    }

    def __init__(self) -> None:
        self.events: list[Event] = []

    def publish(self, event_type: str, payload: dict | None = None) -> Event:
        event = Event(type=str(event_type), payload=payload or {})
        self.events.append(event)
        return event

    def filter(self, event_type: str) -> list[Event]:
        return [event for event in self.events if event.type == event_type]


