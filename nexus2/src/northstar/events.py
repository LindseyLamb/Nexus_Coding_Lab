from dataclasses import dataclass
from typing import Protocol
from .errors import *

EVENT_BUSNAME_GENERAL = "eventbus.general"
EVENT_BUSNAME_AUDIT = "eventbus.audit"

@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    customer_id: str
    payload: dict[str, str]


class EventSubscriber(Protocol):
    def handle(self, event: DomainEvent) -> None:
        ...


class EventBus:
    """Small observer-style event dispatcher."""


    def __init__(self) -> None:
        self.published: list[DomainEvent] = []
        self._bus_subscribers = {EVENT_BUSNAME_GENERAL : [], EVENT_BUSNAME_AUDIT : []}

    def subscribe(self, subscriber: EventSubscriber, bus_name = EVENT_BUSNAME_GENERAL) -> None:
        if bus_name not in self._bus_subscribers:
            raise BusNameError(f"Bus name {bus_name} is not valid")
        self._bus_subscribers[bus_name].append(subscriber)

    def publish(self, event: DomainEvent, bus_name = EVENT_BUSNAME_GENERAL) -> None:
        if bus_name not in self._bus_subscribers:
            raise BusNameError(f"Bus name {bus_name} is not valid")

        if bus_name == EVENT_BUSNAME_GENERAL:
            self.published.append(event)

        subscribers = self._bus_subscribers[bus_name]

        for subscriber in subscribers:
            subscriber.handle(event)
