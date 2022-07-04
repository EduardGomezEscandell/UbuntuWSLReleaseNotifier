import datetime
import unittest
import subprocess
import time

import notify


class TestUpgradeNotifier(unittest.TestCase):
    def testAvailableUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"New release '21.10' available.\n"                                 \
                        r"Run 'do-release-upgrade' to upgrade to it.'\""
        errcode, msg = notify.upgrade_message("printf", fake_response)
        expected = "Release available\n"                                                    \
                   "=================\n"                                                    \
                   "A new release of Ubuntu is available: Ubuntu 21.10\n"                   \
                   "To know more, run do-release-upgrade\n"                                 \
                   "To change the types of updates you are notified about,\n"                \
                   "read and modify file /etc/update-manager/release-upgrades"
        self.assertEqual(errcode, 0)
        self.assertEqual(msg, expected)

    def testUnAvailableUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"There is no development version of an LTS available.\n"           \
                        r"To upgrade to the latest non-LTS development release \n"          \
                        r"set Prompt=normal in /etc/update-manager/release-upgrades.'\""
        errcode, msg = notify.upgrade_message("printf", fake_response)
        self.assertEqual(errcode, 0)
        self.assertFalse(msg)

    def testDisabledUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"In /etc/update-manager/release-upgrades Prompt \n"                \
                        r"is set to never so upgrading is not possible.\""
        errcode, msg = notify.upgrade_message("printf", fake_response)
        self.assertEqual(errcode, 0)
        self.assertFalse(msg)

    def testFailure(self):
        errcode, msg = notify.upgrade_message("python3", "-c", "raise RuntimeError('test')")
        self.assertEqual(errcode, 1)
        self.assertIsInstance(msg, subprocess.CalledProcessError)

    def testTimeout(self):
        start = time.time()
        errcode, msg = notify.upgrade_message("sleep", "5", timeout=1)
        time_elapsed_ms = 1000*(time.time() - start)

        self.assertEqual(errcode, 1)
        self.assertIsInstance(msg, subprocess.TimeoutExpired)
        self.assertLessEqual(time_elapsed_ms, 1500)

    class __RedirectTimestampIO:
        "Dependency injection to avoid touching the filesystem"
        def __init__(self, time: datetime.datetime = datetime.datetime.now()) -> None:
            self.writer = notify._write_timestamp
            self.reader = notify._LazyDatetime.get
            self.time = time

        def __enter__(self):
            notify._write_timestamp = lambda *_: None
            notify._LazyDatetime.get = lambda *_: self.time
            return self

        def __exit__(self, *_):
            notify._write_timestamp = self.writer
            notify._LazyDatetime.get = self.reader

    def testcooldown(self):
        now = datetime.datetime.now().astimezone()
        two_minutes_ago = now - datetime.timedelta(0, 140)
        two_hours_ago = now - datetime.timedelta(0, 8000)
        two_days_ago = now - datetime.timedelta(2)
        two_weeks_ago = now - datetime.timedelta(14)
        two_months_ago = now - datetime.timedelta(70)
        two_years_ago = now - datetime.timedelta(800)
        with self.__RedirectTimestampIO() as tIO:
            tIO.time = two_minutes_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertFalse(notify._check_cooldown("hour"))
            self.assertFalse(notify._check_cooldown("day"))
            self.assertFalse(notify._check_cooldown("week"))
            self.assertFalse(notify._check_cooldown("month"))
            self.assertFalse(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))
            tIO.time = two_hours_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertTrue(notify._check_cooldown("hour"))
            self.assertFalse(notify._check_cooldown("day"))
            self.assertFalse(notify._check_cooldown("week"))
            self.assertFalse(notify._check_cooldown("month"))
            self.assertFalse(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))
            tIO.time = two_days_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertTrue(notify._check_cooldown("hour"))
            self.assertTrue(notify._check_cooldown("day"))
            self.assertFalse(notify._check_cooldown("week"))
            self.assertFalse(notify._check_cooldown("month"))
            self.assertFalse(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))
            tIO.time = two_weeks_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertTrue(notify._check_cooldown("hour"))
            self.assertTrue(notify._check_cooldown("day"))
            self.assertTrue(notify._check_cooldown("week"))
            self.assertFalse(notify._check_cooldown("month"))
            self.assertFalse(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))
            tIO.time = two_months_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertTrue(notify._check_cooldown("hour"))
            self.assertTrue(notify._check_cooldown("day"))
            self.assertTrue(notify._check_cooldown("week"))
            self.assertTrue(notify._check_cooldown("month"))
            self.assertFalse(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))
            tIO.time = two_years_ago
            self.assertTrue(notify._check_cooldown("none"))
            self.assertTrue(notify._check_cooldown("hour"))
            self.assertTrue(notify._check_cooldown("day"))
            self.assertTrue(notify._check_cooldown("week"))
            self.assertTrue(notify._check_cooldown("month"))
            self.assertTrue(notify._check_cooldown("year"))
            self.assertFalse(notify._check_cooldown("inf"))


if __name__ == '__main__':
    unittest.main()
