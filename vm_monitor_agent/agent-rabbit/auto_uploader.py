# -*- coding: utf-8 -*-

from vm_monitor_agent.common import MyThread
from vm_monitor_agent import swift
from db import DB

from os import path
import time
import logging

LOG = logging.getLogger(__name__)

class AutoUploader(MyThread):
    def __init__(self, monitor, interval):
        super(AutoUpload, self).__init__('AutoUploader', 2)
        self._monitor = monitor
        self._interval = interval

    def work(self):
        q = self._monitor.get_changed_files()
        if len(q) != 0:
            for filepath in q:
                container_id, object_id = DB.get_ids_by_localpath(filepath)
                info = DB.get_info()
                filename = path.basename(filepath)
                swift.upload_object({
                    'user': info['usr'],
                    'key': info['pwd'],
                    'auth_url': info['auth_url'],
                    'tenant_name': info['tenant_name'],
                    'container_name': container_id,
                    'object_name': object_id,
                    'orig_file_name': filename
                }, {
                    'upload_file': (filename, open(filepath, 'rb'))
                })
        time.sleep(self._interval)


