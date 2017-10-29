# -*- coding: utf-8 -*-

from settings import app_data_root

from os import path
import sqlite3
import logging

LOG = logging.getLogger(__name__)


class _Message(object):
    def __init__(self):
        self.conn = sqlite3.connect(path.join(app_data_root, 'msgs.db'))

    def __del__(self):
        self.conn.close()

    def new(self, body):
        return __Message(body)
    
    class __Message(object):
        def __init__(self, msg_body):
            self.container_id = msg_body['container_id']
            self.object_id = msg_body['object_id']
            self.username = msg_body['username']
            self.password = msg_body['password']
            self.auth_url = msg_body['auth_url']
            self.tenant_name = msg_body['tenant_name']
            self.token = msg_body['token']

        def save(self):
            try:
                cur = self.conn.cursor()
                cur.execute("INSERT INTO MESSAGES VALUES \
                        (null,%s,%s,%s,%s,%s,%s,%s)" % (\
                        self.container_id, \
                        self.object_id, \
                        self.username, \
                        self.password, \
                        self.auth_url, \
                        self.tenant_name, \
                        self.token))
                self.conn.commit()

                return True
            except Exception, e:
                LOG.error(e)
                return False

        def file_download(self):
            # TODO:
            return True

Message = _Message()

