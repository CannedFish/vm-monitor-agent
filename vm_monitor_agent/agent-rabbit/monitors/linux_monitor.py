# -*- coding: utf-8 -*-

import pyinotify

from base_monitor import DirMonitor

import logging

LOG = logging.getLogger(__name__)

class LinuxDirMonitor(DirMonitor):
    class __EventHandler(pyinotify.ProcessEvent):
        def __init__(self):
            

    def __init__(self, dirname):
        super(LinuxDirMonitor, self).__init__()
        # self._monitor_thread = __MonitorThread(dirname)

    def start_monitor(self):
        pass
        # self._monitor_thread.start()

    def stop_monitor(self):
        pass
        # self._monitor_thread.stop()

    def get_changed_files(self):
        return []
        # return self._monitor_thread.changed_files


