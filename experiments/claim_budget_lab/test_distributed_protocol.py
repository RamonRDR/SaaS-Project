"""Verificações adicionais do protocolo distribuído entre jobs Actions."""
import copy
import unittest

from experiments.claim_budget_lab.distributed_protocol import (
    InvalidEvidence, proposal, reconcile,
)


class DistributedArtifactTests(unittest.TestCase):
    HEAD = "sha-test"
    RUN = "run-123"

    def p(self):
        return [proposal(w, self.HEAD, self.RUN) for w in ("alpha", "beta")]

    def test_budget_cap_and_single_claim(self):
        state = reconcile(self.p(), self.HEAD, self.RUN)
        self.assertEqual(state["ledger"]["claim_winner"], "alpha")
        self.assertEqual(len(state["ledger"]["reservations"]), 4)
        self.assertEqual(sum(x["max_cost_minor"] for x in state["ledger"]["reservations"]), 4)
        self.assertEqual(state["provenance"]["claim_winners"], 1)
        self.assertEqual(state["provenance"]["provider_calls"], 0)

    def test_duplicate_requests_aggregated_once(self):
        report = reconcile(self.p(), self.HEAD, self.RUN)
        ids = [x["request_id"] for x in report["ledger"]["reservations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(report["provenance"]["duplicate_request_ids_deduplicated"], 2)

    def test_unknown_ack_requires_readback_not_retry(self):
        report = reconcile(self.p(), self.HEAD, self.RUN)
        self.assertTrue(report["provenance"]["unknown_ack_reconciled_by_artifact_read"])
        self.assertEqual(report["provenance"]["proposal_acks"]["alpha"], "UNKNOWN_AFTER_PERSIST")

    def test_pre_persist_failure_does_not_enter_ledger(self):
        report = reconcile(self.p(), self.HEAD, self.RUN)
        self.assertTrue(report["provenance"]["lost_before_persist_was_rejected"])
        self.assertNotIn("req-lost", str(report["ledger"]))

    def test_tampered_artifact_rejected(self):
        p = self.p()
        p[1]["requests"].append("malicious")
        with self.assertRaises(InvalidEvidence):
            reconcile(p, self.HEAD, self.RUN)

    def test_wrong_head_rejected(self):
        with self.assertRaises(InvalidEvidence):
            reconcile(self.p(), "other-head", self.RUN)

    def test_incomplete_workers_fail_closed(self):
        with self.assertRaises(InvalidEvidence):
            reconcile(self.p()[:1], self.HEAD, self.RUN)

    def test_duplicate_workers_fail_closed(self):
        p = self.p()
        with self.assertRaises(InvalidEvidence):
            reconcile([p[0], copy.deepcopy(p[0])], self.HEAD, self.RUN)

    def test_swapped_order_yields_same_result(self):
        p = self.p()
        self.assertEqual(reconcile(p, self.HEAD, self.RUN), reconcile(p[::-1], self.HEAD, self.RUN))


if __name__ == "__main__":
    unittest.main()
