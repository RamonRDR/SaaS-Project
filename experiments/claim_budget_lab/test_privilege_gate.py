"""Garante que o laboratório NÃO abra escrita no SaaS principal."""
from dataclasses import replace
import unittest

from experiments.claim_budget_lab.privilege_gate import (
    RuntimeScope, UnsafePermissionScope, authorize_cas_probe
)


SAFE_LAB = RuntimeScope(
    repository="RamonRDR/SaaS-CAS-Lab",
    trusted_branch="experiment/claim-budget-lab",
    event_name="push",
    contents_write=True,
    has_fork_checkout=False,
    imports_external_code=False,
    uses_paid_provider=False,
    job_timeout_minutes=5,
    ref_prefix="refs/heads/experiment/cas-probe-",
    cleanup_enabled=True,
    audit_readback_enabled=True,
    dedicated_repository=True,
)


class PermissionGateTests(unittest.TestCase):
    def test_isolated_repo_may_be_eligible_after_creation(self):
        authorize_cas_probe(SAFE_LAB)

    def test_main_project_is_not_safe_for_contents_write_experiment(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, repository="RamonRDR/SaaS-Project"))

    def test_branch_alone_is_not_isolation(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, dedicated_repository=False))

    def test_pr_event_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, event_name="pull_request_target"))

    def test_external_code_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, has_fork_checkout=True))

    def test_paid_api_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, uses_paid_provider=True))

    def test_unsafe_ref_prefix_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, ref_prefix="refs/heads/main"))

    def test_missing_cleanup_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, cleanup_enabled=False))

    def test_missing_readback_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, audit_readback_enabled=False))

    def test_broad_timeout_refused(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, job_timeout_minutes=60))

    def test_missing_write_is_not_real_cas_probe(self):
        with self.assertRaises(UnsafePermissionScope):
            authorize_cas_probe(replace(SAFE_LAB, contents_write=False))


if __name__ == "__main__":
    unittest.main()
