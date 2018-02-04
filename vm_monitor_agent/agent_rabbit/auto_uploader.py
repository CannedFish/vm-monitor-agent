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
        super(AutoUploader, self).__init__('AutoUploader', 2)
        self._monitor = monitor
        self._interval = interval

    def __new_obj_name(self, filename):
        pos = filename.rfind('.')
        now = time.strftime("%Y%m%d%H%M%S", time.localtime())
        return "%s-%s%s" % (filename[:pos], now, filename[pos:])

    def work(self):
        try:
            q = self._monitor.get_changed_files()
            LOG.info("check changed files: %s", q)
            if len(q) != 0:
                for filepath in q:
                    LOG.info("change file: %s", filepath)
                    ret = DB.get_ids_by_localpath(filepath)
                    if ret is None:
                        LOG.warning("No record about this file: %s", filepath)
                        continue
                    info = DB.get_info()
                    filename = path.basename(filepath)
                    obj_name = self.__new_obj_name(filename)
                    LOG.info("Try to upload file %s to %s/%s" % (filepath, ret[0], obj_name))
                    ret = swift.upload_object('', {
                        'user': info['usr'],
                        'key': info['pwd'],
                        'auth_url': info['auth_url'],
                        'tenant_name': info['tenant_name'],
                        'container_name': ret[0],
                        'object_name': obj_name,
                        'orig_file_name': obj_name,
                        'content_type': ret[3]
                    }, {
                        'upload_file': open(filepath, 'rb')
                    })
                    LOG.info("Upload result: %s" % ret)
            time.sleep(self._interval)
        except Exception, e:
            LOG.error(e)

