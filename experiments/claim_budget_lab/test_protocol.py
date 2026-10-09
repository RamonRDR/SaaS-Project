"""Testes simulados, sem rede, sem secrets, sem dependências de terceiros."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from experiments.claim_budget_lab.model import (
    AmbiguousDispatch, CASConflict, Denied, FakeClock, MockProvider,
    Operation, PaidInferenceLab, SimulatedCASLedger,
)


def utc(year=2026, month=10, day=8, hour=12, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


class UniversalClaimTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock(utc())
        self.provider = MockProvider(cost_minor=3)
        self.lab = PaidInferenceLab(clock=self.clock, provider=self.provider, monthly_limit_minor=40)

    def create(self, *, kind="fork_review", pr=1, head="sha01", author="ramon",
               association="OWNER", attempt=0, eligible=True):
        op = Operation("RamonRDR/SaaS-Project", pr, head, kind, author, association, attempt)
        key = self.lab.enqueue(op)
        if eligible:
            self.lab.eligible(key)
        return key

    def claim_and_budget(self, **kwargs):
        key = self.create(**kwargs)
        self.assertTrue(self.lab.claim(key, "worker-A"))
        self.lab.reserve_budget(key, "worker-A", 9)
        return key

    def test_fork_requires_explicit_trust_for_external_author(self):
        key = self.create(association="NONE", eligible=False)
        with self.assertRaises(Denied):
            self.lab.eligible(key)
        self.lab.approve_external(key)
        self.lab.eligible(key)
        self.assertTrue(self.lab.claim(key, "worker-A"))

    def test_same_repo_review_has_universal_claim(self):
        key = self.claim_and_budget(kind="same_repo_review")
        self.assertEqual(self.lab.dispatch(key, "worker-A"), 3)
        self.assertEqual(len(self.provider.calls), 1)

    def test_remediator_has_universal_claim(self):
        key = self.claim_and_budget(kind="remediator", attempt=2)
        self.assertEqual(self.lab.dispatch(key, "worker-A"), 3)

    def test_all_three_kinds_use_same_claim_protocol(self):
        for i, kind in enumerate(("fork_review", "same_repo_review", "remediator")):
            key = self.create(kind=kind, pr=i + 1, head=f"sha{i}", attempt=0)
            self.assertTrue(self.lab.claim(key, f"worker-{i}"))
            self.lab.reserve_budget(key, f"worker-{i}", 10)
            self.lab.dispatch(key, f"worker-{i}")
        self.assertEqual(self.lab.snapshot()["provider_calls"], 3)

    def test_fork_per_pr_limit_three_in_twenty_four_hours(self):
        for i in range(3):
            self.create(pr=5, head=f"head{i}")
        with self.assertRaises(Denied):
            self.create(pr=5, head="head3")

    def test_fork_external_author_limit_five_across_prs(self):
        for i in range(5):
            key = self.create(pr=20 + i, head=f"head{i}", author="external", association="NONE", eligible=False)
            self.lab.approve_external(key)
            self.lab.eligible(key)
        sixth = self.create(pr=40, head="head6", author="external", association="NONE", eligible=False)
        self.lab.approve_external(sixth)
        with self.assertRaises(Denied):
            self.lab.eligible(sixth)

    def test_enqueue_same_identity_does_not_duplicate_request(self):
        op = Operation("RamonRDR/SaaS-Project", 1, "abc", "fork_review", "ramon")
        self.assertEqual(self.lab.enqueue(op), self.lab.enqueue(op))
        self.assertEqual(self.lab.snapshot()["requests"], 1)

    def test_two_workers_race_for_one_claim_only_one_wins(self):
        key = self.create()
        runs = [f"worker-{i}" for i in range(32)]
        with ThreadPoolExecutor(max_workers=16) as pool:
            result = list(pool.map(lambda run: (run, self.lab.claim(key, run)), runs))
        winners = [run for run, won in result if won]
        self.assertEqual(len(winners), 1)
        self.lab.reserve_budget(key, winners[0], 9)
        for loser in runs:
            if loser != winners[0]:
                with self.assertRaises(Denied):
                    self.lab.reserve_budget(key, loser, 9)
        self.assertEqual(self.lab.snapshot()["reservations"], 1)

    def test_claim_required_before_any_budget_reservation(self):
        key = self.create()
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "worker-A", 9)
        self.assertEqual(self.lab.snapshot()["reservations"], 0)

    def test_budget_reservation_idempotent_for_winner(self):
        key = self.create()
        self.lab.claim(key, "worker-A")
        a = self.lab.reserve_budget(key, "worker-A", 9)
        b = self.lab.reserve_budget(key, "worker-A", 9)
        self.assertEqual(a, b)
        self.assertEqual(self.lab.snapshot()["exposure_by_period"]["2026-10"], 9)
        self.assertEqual(self.lab.snapshot()["reservations"], 1)

    def test_duplicate_request_cannot_send_twice(self):
        key = self.claim_and_budget()
        self.lab.dispatch(key, "worker-A")
        with self.assertRaises(Denied):
            self.lab.dispatch(key, "worker-A")
        self.assertEqual(len(self.provider.calls), 1)

    def test_two_different_prs_race_for_global_budget(self):
        keys = []
        for i in range(10):
            key = self.create(kind="same_repo_review", pr=i + 1, head=f"sha{i}")
            self.lab.claim(key, f"worker-{i}")
            keys.append((key, f"worker-{i}"))
        def attempt(pair):
            try:
                self.lab.reserve_budget(*pair, 9)
                return True
            except Denied:
                return False
        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(attempt, keys))
        self.assertEqual(sum(results), 4)
        self.assertLessEqual(self.lab.snapshot()["exposure_by_period"]["2026-10"], 40)

    def test_crash_after_claim_before_budget_is_fail_closed(self):
        key = self.create()
        self.lab.claim(key, "crashed-worker")
        self.assertFalse(self.lab.claim(key, "recovering-worker"))
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "recovering-worker", 5)
        self.assertEqual(self.lab.snapshot()["provider_calls"], 0)
        self.assertEqual(self.lab.snapshot()["reservations"], 0)

    def test_crash_after_dispatch_conserves_cost_and_blocks_retry(self):
        key = self.claim_and_budget()
        with self.assertRaises(AmbiguousDispatch):
            self.lab.dispatch(key, "worker-A", ambiguous=True)
        with self.assertRaises(Denied):
            self.lab.dispatch(key, "worker-A")
        self.assertEqual(len(self.provider.calls), 1)
        self.assertEqual(self.lab.snapshot()["exposure_by_period"]["2026-10"], 9)

    def test_insufficient_budget_blocks_before_provider(self):
        key = self.create()
        self.lab.claim(key, "worker-A")
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "worker-A", 41)
        self.assertEqual(self.lab.snapshot()["provider_calls"], 0)

    def test_utc_rollover_keeps_claim_and_reauthorizes_finance_only(self):
        self.clock.set(utc(2026, 10, 31, 23, 58))
        key = self.claim_and_budget()
        self.clock.set(utc(2026, 11, 1, 0, 1))
        with self.assertRaises(Denied):
            self.lab.dispatch(key, "worker-A")
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "worker-A", 9)
        new_finance = self.lab.reserve_budget(key, "worker-A", 9, prove_not_sent=True)
        self.assertEqual(new_finance["period"], "2026-11")
        self.assertFalse(self.lab.claim(key, "worker-A"))  # Claim lógico é imutável.
        self.assertEqual(self.lab.dispatch(key, "worker-A"), 3)
        snap = self.lab.snapshot()
        self.assertEqual(snap["reservations"], 2)
        self.assertEqual(snap["exposure_by_period"]["2026-10"], 9)
        self.assertEqual(snap["provider_calls"], 1)

    def test_rollover_with_ambiguous_prior_send_must_not_retry(self):
        self.clock.set(utc(2026, 10, 31, 23, 58))
        key = self.claim_and_budget()
        with self.assertRaises(AmbiguousDispatch):
            self.lab.dispatch(key, "worker-A", ambiguous=True)
        self.clock.set(utc(2026, 11, 1, 0, 1))
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "worker-A", 9, prove_not_sent=True)
        self.assertEqual(len(self.provider.calls), 1)

    def test_utc_boundary_guard_prevents_near_rollover_dispatch(self):
        key = self.claim_and_budget()
        self.clock.set(utc(2026, 10, 31, 23, 59, 50))
        with self.assertRaises(Denied):
            self.lab.dispatch(key, "worker-A")
        self.assertEqual(len(self.provider.calls), 0)

    def test_missing_utc_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.clock.set(datetime(2026, 10, 8))

    def test_stale_snapshot_fails_cas(self):
        ledger = SimulatedCASLedger()
        v = ledger.version
        ledger.update(v, lambda: 1)
        with self.assertRaises(CASConflict):
            ledger.update(v, lambda: 2)

    def test_claim_consumer_cannot_change_after_winner(self):
        key = self.create()
        self.assertTrue(self.lab.claim(key, "original"))
        self.assertFalse(self.lab.claim(key, "replacement"))
        with self.assertRaises(Denied):
            self.lab.reserve_budget(key, "replacement", 9)


if __name__ == "__main__":
    unittest.main()
