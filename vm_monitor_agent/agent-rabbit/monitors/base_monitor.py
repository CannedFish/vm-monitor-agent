# -*- coding: utf-8 -*-
import abc

class DirMonitor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start_monitor(self):
        """start to monitor the given directory"""

    @abc.abstractmethod
    def stop_monitor(self):
        """stop monitoring"""

    @abc.abstractmethod
    def get_changed_files(self):
        """return files changed in an interval"""

