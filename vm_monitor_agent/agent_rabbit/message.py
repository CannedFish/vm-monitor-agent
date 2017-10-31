# -*- coding: utf-8 -*-

from vm_monitor_agent import swift
from db import DB
from settings import dir_to_be_monitored

from os import path
import logging

LOG = logging.getLogger(__name__)


class Message(object):
    def __init__(self, msg_body):
        self.container_id = msg_body['container_id']
        self.object_id = msg_body['object_id']
        self.username = msg_body['username']
        self.password = msg_body['password']
        self.auth_url = msg_body['auth_url']
        self.tenant_name = msg_body['tenant_name']
        self.token = msg_body['token']

        self._msg = DB.msg(self.container_id, self.object_id)
        self._info = DB.info(self.username, \
                self.password, \
                self.auth_url, \
                self.tenant_name, \
                self.token)

    def save(self):
        return self._msg.save()

    def file_download(self):
        ret = swift.get_object({
            'user': self.username,
            'key': self.password,
            'auth_url': self.auth_url,
            'tenant_name': self.tenant_name,
            'container_name': self.container_id,
            'object_name': self.object_id,
            'with_data': 1
        })
        self._msg.update_local_path(path.join(dir_to_be_monitored, ret['name']))

