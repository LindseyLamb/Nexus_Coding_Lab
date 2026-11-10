
from abc import ABC, abstractmethod

class AuditRepository(ABC):
    
    @abstractmethod
    def write(actor_id : str, customer_id: str, reason: str):
        raise NotImplementedError

    def getRecords() -> list[dict]:
        raise NotImplementedError



class InMemoryAudit(AuditRepository):
    audit_records:list[dict]

    def write(actor_id : str, customer_id: str, reason: str):
        list.append({"customer_id":customer_id, "actor_id": actor_id, "reason": reason})

    def getRecords() -> list[dict]:
        return audit_records
