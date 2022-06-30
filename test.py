import unittest
import notify


class TestUpgradeNotifier(unittest.TestCase):
    def testAvailableUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"New release '21.10' available.\n"                                 \
                        r"Run 'do-release-upgrade' to upgrade to it.'\""
        msg = notify.upgrade_message("printf", fake_response)
        expected = "Release available\n"                                                    \
                   "=================\n"                                                    \
                   "A new release of Ubuntu is available: Ubuntu 21.10\n"                   \
                   "To know more, run do-release-upgrade\n"                                 \
                   "To disable or change the frequency of these alerts,\n"                  \
                   "read and modify file /etc/update-manager/release-upgrades"
        self.assertEqual(msg, expected)

    def testUnAvailableUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"There is no development version of an LTS available.\n"           \
                        r"To upgrade to the latest non-LTS development release \n"          \
                        r"set Prompt=normal in /etc/update-manager/release-upgrades.'\""
        msg = notify.upgrade_message("printf", fake_response)
        self.assertFalse(msg)

    def testDisabledUpgrade(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"In /etc/update-manager/release-upgrades Prompt \n"                \
                        r"is set to never so upgrading is not possible.\""
        msg = notify.upgrade_message("printf", fake_response)
        self.assertFalse(msg)

    def testFailure(self):
        fake_response = r"\"Checking for a new Ubuntu release\n"                            \
                        r"^CTraceback (most recent call last):\n"                           \
                        r"  File \"/usr/bin/do-release-upgrade\", line 136, in <module>\n"  \
                        r"    m.downloaded.wait()\n"                                        \
                        r"  File \"/usr/lib/python3.8/threading.py\", line 558, in wait\n"  \
                        r"    signaled = self._cond.wait(timeout)\n"                        \
                        r"  File \"/usr/lib/python3.8/threading.py\", line 302, in wait\n"  \
                        r"    waiter.acquire()\n"                                           \
                        r"KeyboardInterrupt\""
        msg = notify.upgrade_message("printf", fake_response)
        self.assertFalse(msg)


if __name__ == '__main__':
    unittest.main()
