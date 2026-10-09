"""Verifica SOMENTE consistência da evidência versionada, não prova CAS remoto."""
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent

class PersistedGitEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads((HERE / "cas-ledger.json").read_text(encoding="utf-8"))
        self.evidence = json.loads((HERE / "cas-real-evidence.json").read_text(encoding="utf-8"))

    def test_cas_ledger_has_single_winner_and_no_duplicate_reservations(self):
        ledger = self.ledger
        self.assertEqual(ledger["claim_owner"], self.evidence["claim"]["observed_winner"])
        ids = [x["id"] for x in ledger["reservations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, self.evidence["budget"]["observed_reservation_ids"])
        self.assertEqual(ledger["revision"], 1 + len(ids))
        self.assertEqual(sum(x["max_cost_minor"] for x in ledger["reservations"]),
                         self.evidence["budget"]["observed_total_minor"])
        self.assertLessEqual(sum(x["max_cost_minor"] for x in ledger["reservations"]),
                             ledger["monthly_budget_limit"])

    def test_witnesses_are_distinct_siblings_and_limit_is_explicit(self):
        e = self.evidence
        self.assertEqual(len({x["sha"] for x in e["claim"]["candidates"]}), 2)
        self.assertEqual(len({x["sha"] for x in e["budget"]["initial_proposals"]}), 6)
        self.assertEqual(e["budget"]["budget_limit_minor"], 4)
        self.assertEqual(e["budget"]["application_policy_denied_before_write"], ["op-05", "op-06"])
        self.assertFalse(e["stale_expected_descendant"]["head_changed"])
        self.assertFalse(e["controls"]["ref_update_force"])
        self.assertEqual(e["controls"]["paid_ai_calls"], 0)
        self.assertTrue(any("UNKNOWN" in x for x in e["controls"]["caveats"]))

if __name__ == "__main__":
    unittest.main()
