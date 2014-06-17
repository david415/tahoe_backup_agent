import twisted
from twisted.internet import task, defer


class BackupManager(object):
    """
    I execute backup commands and manage the backup schedule.

    The schedule changes dynamically depending on the timing of the observed writes.
    My associate... a filesystem observer tells me when my backup source directory tree
    gets changed and therefore needs a backup by calling my `scheduleBackup` method.

    I promise to perform a backup sometime after my `scheduleBackup` method is called.
    I will try not to perform a backup in the middle of many observed writes.

    Although I am a class written in a generic way I am really meant
    to be used with Tahoe-LAFS... We should essentially be scheduling
    backups using the functionality of the "tahoe backup" command;
    This should probably happen in the tahoe gateway node... however this
    class *could* be used by a standalone python app that for instance
    schedules the `rsync` command to run.
    """
    def __init__(self, reactor=None, soonDuration=None, laterDuration=None, soonCommand=None, laterCommand=None):
        """
        :param reactor:
            :api:`twisted.internet.interfaces.IReactorTime` provider

        :param soonDuration:
            The number of seconds after an observed write when a backup
            should take place. Cancelled if either a "later backup" is performed
            or if another write is observed.

        :param laterDuration:
            The number of seconds after the initial observed write when a backup is guaranteed.
            Cancelled if a "soon backup" is performed because of a later observed write.

        :param soonCommand:
            The backup command to execute when our "soon" schedule executes.

        :param laterCommand:
            The backup command to execute when our "later" schedule executes.
            This can of course be an identical value to "soonCommand".
        """
        self.reactor = reactor
        self.soonDuration = soonDuration
        self.laterDuration = laterDuration
        self.soonCommand = soonCommand
        self.laterCommand = laterCommand

        self.backupSoon = None
        self.backupLater = None

    def trapCancel(self, failure):
        """
        :param failure:
            The deferred's errback failure

        I sit on the deferred's errback and trap the deferred's cancellation error
        so that it isn't surfaced to the user.
        """
        fail.trap(defer.CancelledError)

    def scheduleBackup(self):
        """
        My "filesystem observer" associate object must call this method to
        notify me that my backup source directory tree has been modified.

        I promise to perform a backup in the future...
        no later than laterDuration... but possibly as soon as soonDuration.
        """
        if self.backupLater is None:
            self.backupLater = task.deferLater(self.reactor, self.laterDuration, self.laterBackup)
            self.backupLater.addErrback(self.trapCancel)
        else:
            self.backupSoon.cancel()
        self.backupSoon = task.deferLater(self.reactor, self.soonDuration, self.soonBackup)
        self.backupSoon.addErrback(self.trapCancel)

    def soonBackup(self):
        """
        I will execute the "soon backup command" after cancelling
        the "later backup".
        """
        assert self.backupLater is not None

        self.backupLater.cancel()
        self.backupLater = None

        self.soonCommand()
        self.backupSoon = None

    def laterBackup(self):
        """
        I will execute the "later backup command" after cancelling
        the "soon backup".
        """
        assert self.backupSoon is not None

        self.backupSoon.cancel()
        self.backupSoon = None

        self.laterCommand()
        self.backupLater = None
