
what is this?
=============

this here is a brain dump.


objective
---------

Tahoe-LAFS needs a backup agent to schedule and invoke backups...
the agent shall observe directory tree changes from the notify syscall.

Tasks scheduling is optimized to not invoke "tahoe backup" during
a time period with my write events to the directory tree.

This should all be implemented in the tahoe gateway process... not in a standalone program.
The reason is because we need to expose the percentage backup transfer progress to the user...
and to do this we need to be inside the gateway. The progress interface should be written in
a sufficiently flexible and generic way such that it can be used by many different things...

Tails for instance should/could have a applet widget that displays an on screen backup progress.



