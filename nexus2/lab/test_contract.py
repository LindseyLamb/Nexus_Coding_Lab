"""New teaching requirements, not original repository tests."""
import unittest
from adapter import build, audit_records
from northstar.auth import Actor
from northstar.errors import AuthorizationError, CustomerNotFoundError

SECRET = "PRIVATE-REASON-42"
class Contract(unittest.TestCase):
    def setUp(self): self.s = build()
    def command(self, role="manager", reason=SECRET, customer_id="c1"):
        return self.s.lifecycle.deactivate(Actor("u-review", role), customer_id, reason)

    def test_01_reason_stays_out_of_public_event(self):
        self.command()
        self.assertEqual(len(self.s.bus.published), 1)
        event = self.s.bus.published[0]
        self.assertEqual(event.event_type, "customer.deactivated")
        self.assertEqual(event.customer_id, "c1")
        self.assertEqual(event.payload.get("email"), "case@example.com")
        self.assertNotIn(SECRET, repr(self.s.bus.published))
        self.assertNotIn("reason", event.payload)

    def test_02_customer_gets_generic_notification(self):
        self.command()
        self.assertEqual(self.s.client.sent_messages,
            [("case@example.com", "Your Atlas account has been deactivated.")])

    def test_03_reason_is_retained_in_internal_audit(self):
        self.command(reason="  " + SECRET + "  ")
        self.assertEqual(audit_records(self.s),
            [{"customer_id":"c1", "actor_id":"u-review", "reason":SECRET}])

    def test_04_success_preserves_customer_result(self):
        result = self.command(role="admin")
        self.assertEqual(result.customer_id, "c1")
        self.assertFalse(result.active)
        self.assertFalse(self.s.repository.get("c1").active)

    def test_05_denied_command_has_no_effects(self):
        with self.assertRaises(AuthorizationError): self.command(role="viewer")
        self.assert_no_effects()

    def test_06_short_reason_has_no_effects(self):
        with self.assertRaises(ValueError): self.command(reason="  no  ")
        self.assert_no_effects()

    def test_07_missing_customer_has_no_effects(self):
        with self.assertRaises(CustomerNotFoundError): self.command(customer_id="missing")
        self.assert_no_effects()

    def assert_no_effects(self):
        self.assertTrue(self.s.repository.get("c1").active)
        self.assertEqual(self.s.bus.published, [])
        self.assertEqual(self.s.client.sent_messages, [])
        self.assertEqual(audit_records(self.s), [])
        
    def test_08_notification_failure_does_not_erase_audit(self):
        def fail(*args): raise RuntimeError("simulated notification failure")
        self.s.client.send = fail
        with self.assertRaises(RuntimeError): self.command()
        self.assertFalse(self.s.repository.get("c1").active)
        self.assertEqual(audit_records(self.s),
            [{"customer_id":"c1", "actor_id":"u-review", "reason":SECRET}])
        self.assertNotIn(SECRET, repr(self.s.bus.published))
        self.assertEqual(self.s.client.sent_messages, [])

    def test_09_second_public_subscriber_cannot_see_reason(self):
        # A second public subscriber should only receive
        # the sanitized customer.deactivated event.
        received_events = []

        class SecondSubscriber:
            def handle(self, event):
                received_events.append(event)

        self.s.bus.subscribe(SecondSubscriber())

        self.command(reason="  " + SECRET + "  ")

        self.assertEqual(len(received_events), 1)

        event = received_events[0]

        self.assertEqual(event.event_type, "customer.deactivated")
        self.assertEqual(event.customer_id, "c1")
        self.assertEqual(event.payload["email"], "case@example.com")

        # Confidential information must not reach
        # any general-channel subscriber.
        self.assertNotIn("reason", event.payload)
        self.assertNotIn(SECRET, repr(received_events))

        # The internal audit must still retain the reason.
        self.assertEqual(
            audit_records(self.s),
            [{
                "customer_id": "c1",
                "actor_id": "u-review",
                "reason": SECRET
            }]
        )

if __name__ == "__main__": unittest.main()
