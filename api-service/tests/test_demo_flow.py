"""Pruebas sin red para el flujo de prevención de Guardián."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.infrastructure.database import GuardianStore
from app.services.risk_engine.rules import assess_transfer
from app.services.risk_engine.state import TransactionEvent
from app.services.simulation import run_simulation


class DemoFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self._temporary_directory.name) / "guardian-test.db"
        self.store = GuardianStore(database_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    @staticmethod
    def _demo_account(user_id: str) -> str:
        return f"demo:{user_id}:guardian-demo-simulation"

    def test_app_scam_is_paused_and_can_be_cancelled(self) -> None:
        result = run_simulation(
            account_id=self._demo_account("rosa-elena"),
            now=datetime(2026, 9, 12, tzinfo=timezone.utc),
            store=self.store,
        )

        self.assertEqual(result.processed, 8)
        self.assertGreaterEqual(result.alerts_generated, 2)
        operations = self.store.recent_operations()
        self.assertEqual(len(operations), 8)

        suspicious_transfer = next(
            item for item in operations if item.kind == "transfer"
        )
        self.assertEqual(suspicious_transfer.status, "pending_review")
        self.assertGreaterEqual(suspicious_transfer.score, 60)
        self.assertTrue(
            any("Beneficiario nuevo" in reason for reason in suspicious_transfer.reasons)
        )

        resolved = self.store.resolve_operation(suspicious_transfer.id, "cancelled")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.status, "cancelled")
        self.assertEqual(self.store.recent_cases("rosa-elena"), [])
        self.assertEqual(self.store.recent_audit_events("rosa-elena")[0]["action"], "review_cancelled")

    def test_reset_removes_only_demo_account_data(self) -> None:
        account_id = self._demo_account("rosa-elena")
        run_simulation(account_id=account_id, store=self.store)
        self.store.reset_demo(account_id)

        self.assertEqual(self.store.recent_operations(), [])
        self.assertEqual(self.store.recent_alerts(), [])

    def test_confirmation_executes_once_and_pressure_opens_case(self) -> None:
        run_simulation(account_id=self._demo_account("rosa-elena"), store=self.store, user_id="rosa-elena")
        transfer = next(item for item in self.store.recent_operations() if item.kind == "transfer")

        confirmed = self.store.resolve_operation(transfer.id, "confirmed")
        self.assertIsNotNone(confirmed)
        self.assertEqual(confirmed.status, "confirmed")
        events = self.store.events_for(transfer.account_id, datetime.now(timezone.utc))
        self.assertEqual(len(events), 8)
        self.assertIsNone(self.store.resolve_operation(transfer.id, "confirmed"))
        self.assertEqual(self.store.recent_cases("rosa-elena"), [])
        self.assertEqual(self.store.recent_audit_events("rosa-elena")[0]["action"], "review_confirmed")

        pressure_account = "demo:rosa-elena:pressure-demo"
        run_simulation(account_id=pressure_account, store=self.store, user_id="rosa-elena")
        pressured = next(item for item in self.store.recent_operations() if item.account_id == pressure_account and item.kind == "transfer")
        reported = self.store.resolve_operation(pressured.id, "reported_pressure")
        self.assertIsNotNone(reported)
        self.assertEqual(reported.status, "reported_pressure")
        self.assertEqual(len(self.store.recent_cases("rosa-elena")), 1)
        self.assertEqual(self.store.recent_audit_events("rosa-elena")[0]["action"], "review_reported_pressure")
        self.assertEqual(self.store.recent_cases(None)[0]["user_id"], "rosa-elena")
        self.assertEqual(self.store.recent_audit_events(None)[0]["action"], "review_reported_pressure")

    def test_timeline_is_isolated_between_demo_users(self) -> None:
        run_simulation(account_id=self._demo_account("rosa-elena"), store=self.store, user_id="rosa-elena")
        run_simulation(account_id=self._demo_account("analyst-demo"), store=self.store, user_id="analyst-demo")

        self.assertEqual(len(self.store.recent_operations("rosa-elena")), 8)
        self.assertEqual(len(self.store.recent_operations("analyst-demo")), 8)
        self.assertEqual(len(self.store.recent_operations(None)), 16)
        rosa_alerts = {alert.id for alert in self.store.recent_alerts("rosa-elena")}
        analyst_alerts = {alert.id for alert in self.store.recent_alerts("analyst-demo")}
        self.assertTrue(rosa_alerts)
        self.assertTrue(analyst_alerts)
        self.assertTrue(rosa_alerts.isdisjoint(analyst_alerts))
        self.assertEqual(len(self.store.recent_alerts(None)), len(rosa_alerts) + len(analyst_alerts))

    def test_context_signals_can_pause_a_modest_new_transfer(self) -> None:
        now = datetime(2026, 9, 12, tzinfo=timezone.utc)
        prior = [TransactionEvent("account", 100.0, now)]
        assessment = assess_transfer(
            600.0,
            "new-beneficiary",
            prior,
            now,
            new_device=True,
            beneficiary_flagged=True,
        )
        self.assertEqual(assessment.level, "high")
        self.assertTrue(any("Dispositivo nuevo" in reason for reason in assessment.reasons))


if __name__ == "__main__":
    unittest.main()
