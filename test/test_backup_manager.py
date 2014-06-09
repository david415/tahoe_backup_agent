#!/usr/bin/python

from twisted.trial import unittest
from twisted.internet import task

# XXX
from backup_manager import BackupManager


class BackupManagerTestScheduler(unittest.TestCase):

    def setUp(self):
        self.soon = 0
        self.later = 0
        self.clock = task.Clock()
        self.myBackup = BackupManager(self.clock,
                                      soonDuration=3,
                                      laterDuration=5,
                                      soonCommand=self.soonBackup,
                                      laterCommand=self.laterBackup)

    def soonBackup(self):
        self.soon += 1

    def laterBackup(self):
        self.later += 1

    def _testSoon(self):
        self.myBackup.scheduleBackup()
        self.clock.advance(3)

    def _testLater(self):
        self.myBackup.scheduleBackup()
        self.clock.advance(1)
        self.myBackup.scheduleBackup()
        self.clock.advance(1)
        self.myBackup.scheduleBackup()
        self.clock.advance(3)

    def testOnlySoon(self):
        self._testSoon()
        self.assertEqual(self.soon, 1)
        self.assertEqual(self.later, 0)

    def testOnlyLater(self):
        self._testLater()
        self.assertEqual(self.soon, 0)
        self.assertEqual(self.later, 1)

    def testSoonAndLater(self):
        self._testSoon()
        self._testLater()
        self.assertEqual(self.soon, 1)
        self.assertEqual(self.later, 1)

    def test2Soon(self):
        self._testSoon()
        self._testSoon()
        self.assertEqual(self.soon, 2)
        self.assertEqual(self.later, 0)

    def test2Later(self):
        self._testLater()
        self._testLater()
        self.assertEqual(self.soon, 0)
        self.assertEqual(self.later, 2)

    def test2Later1Soon(self):
        self._testLater()
        self._testLater()
        self._testSoon()
        self.assertEqual(self.soon, 1)
        self.assertEqual(self.later, 2)

    def test2Later2Soon(self):
        self._testLater()
        self._testLater()
        self._testSoon()
        self._testSoon()
        self.assertEqual(self.soon, 2)
        self.assertEqual(self.later, 2)
