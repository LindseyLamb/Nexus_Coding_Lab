"""Lab wiring, not upstream Nexus code. Adapt this to your design.
Do not manufacture audit records in this adapter: production code must write them.
"""
from types import SimpleNamespace
from northstar.auth import AuthorizationService
from northstar.events import *
from northstar.models import Customer
from northstar.notifications import NotificationClient, CustomerNotificationSubscriber
from northstar.repository import InMemoryCustomerRepository
from northstar.services import CustomerLifecycleService
from northstar.audit import *
import tempfile
import os



def build():
    repository = InMemoryCustomerRepository()
    repository.save(Customer("c1", "Case Customer", "case@example.com"))
    bus = EventBus()
    client = NotificationClient()
    bus.subscribe(CustomerNotificationSubscriber(client))

    # Get a temp file to store
    if Path("TempAuditLog.json").exists():
        os.remove("TempAuditLog.json")

    audit_log = FileBackedAudit("TempAuditLog.json")
    bus.subscribe(AuditSubcriber(audit_log), EVENT_BUSNAME_AUDIT)
    lifecycle = CustomerLifecycleService(repository, AuthorizationService(), bus)
    return SimpleNamespace(repository=repository, bus=bus, client=client,
                           lifecycle=lifecycle, audit=[], audit_log=audit_log)


def audit_records(system) -> list:
    # Return a list of mappings with customer_id, actor_id, reason.
    # Map your real audit objects here if necessary. Never synthesize the answer.
    return system.audit_log.getRecords()
