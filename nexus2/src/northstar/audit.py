
from abc import ABC, abstractmethod
from .events import EventSubscriber, DomainEvent

class AuditRepository(ABC):
    @abstractmethod
    def writeDeactivation(self, actor_id : str, customer_id: str, reason: str):
        raise NotImplementedError

    @abstractmethod
    def getRecords(self) -> list[dict]:
        raise NotImplementedError



class InMemoryAudit(AuditRepository):

    def __init__(self):
        self.audit_records = []

    def writeDeactivation(self, actor_id : str, customer_id: str, reason: str):
        self.audit_records.append({"customer_id":customer_id, "actor_id": actor_id, "reason": reason})

    def getRecords(self) -> list[dict]:
        return self.audit_records

class AuditSubcriber(EventSubscriber):

    def __init__(self, repo: AuditRepository):
        self._repo = repo

    def handle(self, event: DomainEvent) -> None:
        if(event.event_type == "customer.deactivated"):
            self._repo.writeDeactivation(event.payload["actor_id"], event.customer_id, event.payload["reason"])
        