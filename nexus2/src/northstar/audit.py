
from abc import ABC, abstractmethod
from .events import EventSubscriber, DomainEvent
import json
from pathlib import Path

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



class FileBackedAudit(InMemoryAudit):

    def __init__(self, filename:str) -> None:
        super().__init__()
        self.filename = filename

        # Read back the file if it exists, otherwise create it
        file = None
        if Path(filename).exists():
            data = None
            with open(filename, "r") as f:
                data = json.load(f)
            self.audit_records = data

    def __del__(self):
        with open(self.filename, "w") as f:
            json.dump(self.audit_records, f)
        


    def writeDeactivation(self, actor_id : str, customer_id: str, reason: str):
        super().writeDeactivation(actor_id, customer_id, reason)



class AuditSubcriber(EventSubscriber):

    def __init__(self, repo: AuditRepository):
        self._repo = repo

    def handle(self, event: DomainEvent) -> None:
        if(event.event_type == "customer.deactivated"):
            self._repo.writeDeactivation(event.payload["actor_id"], event.customer_id, event.payload["reason"])
        