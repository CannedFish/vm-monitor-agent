# -*- coding: utf-8 -*-

import win32con
import win32file

from vm_monitor_agent.common import MyThread
from base_monitor import DirMonitor
from vm_monitor_agent.agent_rabbit.settings import dir_to_be_monitored

from os import path
import logging

LOG = logging.getLogger(__name__)

class MonitorThread(MyThread):
	def __init__(self, dirname):
		super(MonitorThread, self).__init__('WinDirMonitor', 1)
		self.dir_ins = win32file.CreateFile(
				dirname,
				0x0001, # FILE_List_DIRECTORY
				win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
				None,
				win32con.OPEN_EXISTING,
				win32con.FILE_FLAG_BACKUP_SEMANTICS,
				None
			)

		self.ACTIONS = {
			1: "Created",
			2: "Deleted",
			3: "Updated",
			4: "Renamed from something",
			5: "Renamed to something"
		}

		self._queue = []

	def work(self):
		results = win32file.ReadDirectoryChangesW(
				self.dir_ins,
				1024,
				True,
				win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
				win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
				win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
				win32con.FILE_NOTIFY_CHANGE_SIZE |
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
				win32con.FILE_NOTIFY_CHANGE_SECURITY,
				None,
				None
			)
		for action, filename in results:
			full_filename = path.join(dir_to_be_monitored, filename)
			# print full_filename, self.ACTIONS.get(action, "Unknown")
			if action == 3: 
				self._queue.append(full_filename)
            # TODO: update localpath when action 4 or 5 happened.

	@property
	def changed_files(self):
		q = [f for f in self._queue]
		self._queue = []
		return set(q)


class WinDirMonitor(DirMonitor):
    def __init__(self, dirname):
        super(WinDirMonitor, self).__init__()
        self._monitor_thread = MonitorThread(dirname)

    def start_monitor(self):
        self._monitor_thread.start()

    def stop_monitor(self):
        self._monitor_thread.stop()

    def get_changed_files(self):
        return self._monitor_thread.changed_files

