# -*- coding: utf-8 -*-

import pyinotify

from base_monitor import DirMonitor

import logging

LOG = logging.getLogger(__name__)

class LinuxDirMonitor(DirMonitor):
    _queue = []

    class __EventHandler(pyinotify.ProcessEvent):
        def __init__(self):
            super(__EventHandler, self).__init__()

        def process_IN_MODIFY(self, event):
            LinuxDirMonitor._queue.append(event.pathname)

        def process_default(self, event):
            LOG.info("%s, %s" % (event.pathname, event.maskname))

    def __init__(self, dirname):
        super(LinuxDirMonitor, self).__init__()
        self._wm = pyinotify.WatchManager()
        self._stat = pyinotify.Stats()
        self._dirname = dirname
        self._notifier = pyinotify.ThreadedNotifier(self._wm, \
                default_proc_func=__EventHandler(s))

    def start_monitor(self):
        LOG.info("start monitor")
        self._notifier.start()
        self.wm.add_watch(self._dirname, pyinotify.ALL_EVENTS, \
                rec=True, auto_add=True)

    def stop_monitor(self):
        LOG.info("stop monitor")
        self.notifier.stop()

    def get_changed_files(self):
        q = [f for f in LinuxDirMonitor._queue]
        LinuxDirMonitor._queue = []
        return q


