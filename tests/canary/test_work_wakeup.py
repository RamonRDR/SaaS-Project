"""Testes do contrato de correspondência exata do wake-up."""

import unittest

from work_wakeup import is_valid_wakeup


class WakeupValidationTests(unittest.TestCase):
    def test_exact_marker_is_valid(self):
        self.assertTrue(is_valid_wakeup("MODE_A_DEV_CANARY_TEST_20261013"))

    def test_different_letters_are_invalid(self):
        for message in (
            "mode_a_dev_canary_test_20261013",
            "MODE_A_DEV_CANARY_TEST_20261013".replace("DEV", "Dev"),
            "MODE_A_DEV_CANARY_TAST_20261013",
        ):
            with self.subTest(message=message):
                self.assertFalse(is_valid_wakeup(message))

    def test_extra_spaces_are_invalid(self):
        marker = "MODE_A_DEV_CANARY_TEST_20261013"
        for message in (" " + marker, marker + " ", marker + "  ", "\t" + marker):
            with self.subTest(message=message):
                self.assertFalse(is_valid_wakeup(message))

    def test_line_breaks_are_invalid(self):
        marker = "MODE_A_DEV_CANARY_TEST_20261013"
        for message in (
            "\n" + marker,
            marker + "\n",
            marker + "\r\n",
            marker.replace("DEV", "DEV\n"),
        ):
            with self.subTest(message=message):
                self.assertFalse(is_valid_wakeup(message))

    def test_other_contents_are_invalid(self):
        for message in ("", "MODE_A_WAKEUP_TEST_20261013", "MODE_A_DEV_CANARY_TEST_20261014"):
            with self.subTest(message=message):
                self.assertFalse(is_valid_wakeup(message))


if __name__ == "__main__":
    unittest.main()
