import unittest
import notify

class TestUpgradeNotifier(unittest.TestCase):

    def testAvailableUpgrade(self):
        msg = notify.upgrade_message("printf", r"\"Checking for a new Ubuntu release\nNew release '21.10' available.\nRun 'do-release-upgrade' to upgrade to it.'\"")
        expected = "Release available\n=================\nA new release of Ubuntu is available: Ubuntu 21.10\nTo know more, run do-release-upgrade\nTo disable or change the frequency of these alerts,\nread and modify file /etc/update-manager/release-upgrades"
        self.assertEqual(msg, expected)
    
    def testUnAvailableUpgrade(self):
        msg = notify.upgrade_message("printf", r"\"Checking for a new Ubuntu release\nThere is no development version of an LTS available.\nTo upgrade to the latest non-LTS development release \nset Prompt=normal in /etc/update-manager/release-upgrades.'\"")
        self.assertEqual(msg, None)

    def testDisabledUpgrade(self):
        msg = notify.upgrade_message("printf", r"\"Checking for a new Ubuntu release\nIn /etc/update-manager/release-upgrades Prompt \nis set to never so upgrading is not possible.\"")
        self.assertEqual(msg, None)

if __name__ == '__main__':
    unittest.main()