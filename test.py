import unittest
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
                   "To disable or change the frequency of these alerts,\n"                  \
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
        self.assertIsInstance(msg, Exception)


if __name__ == '__main__':
    unittest.main()
