# -*- coding: utf-8 -*-

from settings import app_data_root

from os import path
import sqlite3
import logging

LOG = logging.getLogger(__name__)

class _DB(object):
    def __init__(self):
        self._conn = sqlite3.connect(path.join(app_data_root, 'msgs.db'))
        self._info = self._init_info()

    def __del__(self):
        self._conn.close()

    def msg(self, container_id, object_id):
        return _DB.__MSG(container_id, object_id, self._conn)

    def get_ids_by_localpath(self, local_path):
        try:
            cur = self._conn.cursor()
            ret = cur.execute("SELECT container_id, object_id \
                    FROM MESSAGES WHERE local_path='%s'" % local_path)
            return ret.fetchone()
        except Exception, e:
            LOG.error(e)

    def _init_info(self):
        try:
            cur = self._conn.cursor()
            ret = cur.execute("SELECT usr,pwd,auth_url,tenant_name,token FROM INFO").fetchone()
            LOG.debug(ret)
            return {
                'usr': ret[0],
                'pwd': ret[1],
                'auth_url': ret[2],
                'tenant_name': ret[3],
                'token': ret[4]
            }
        except Exception, e:
            print "_init_info:", e
            LOG.error(e)
            return {
                'usr': '',
                'pwd': '',
                'auth_url': '',
                'tenant_name': '',
                'token': ''
            }

    def info(self, usr, pwd, auth_url, tenant_name, token):
        # Table: (usr, pwd, auth_url, tenant_name, token)
        update = False
        for key, value in zip(['usr', 'pwd', 'auth_url', 'tenant_name', 'token'], \
                [usr, pwd, auth_url, tenant_name, token]):
            if value != self._info[key]:
                self._info[key] = value
                update = True
        if update:
            try:
                cur = self._conn.cursor()
                cur.execute("DELETE FROM INFO")
                cur.execute("INSERT INTO INFO VALUES ('%s','%s','%s','%s','%s')" \
                        % (usr, pwd, auth_url, tenant_name, token))
                self._conn.commit()
            except Exception, e:
                print "info:", e
                LOG.error(e)

    def get_info(self):
        return self._info

    class __MSG(object):
        def __init__(self, container_id, object_id, conn):
            self._container_id = container_id
            self._object_id = object_id
            self._local_path = ''
            self._conn = conn

        def save(self):
            try:
                # Table: (id, container_id, object_id, timestramp, local_path)
                cur = self._conn.cursor()
                cur.execute("INSERT INTO MESSAGES (container_id,object_id,local_path) \
                        VALUES ('%s','%s','%s')" % (\
                        self._container_id, \
                        self._object_id, \
                        self._local_path))
                self._conn.commit()
                return True
            except Exception, e:
                print "save:", e
                LOG.error(e)
                return False

        def update_local_path(self, local_path):
            try:
                self._local_path = local_path
                cur = self._conn.cursor()
                cur.execute("UPDATE MESSAGES SET local_path='%s' \
                        where container_id='%s' and object_id='%s'" \
                        % (local_path, self._container_id, self._object_id))
                self._conn.commit()
                return True
            except Exception, e:
                print "update_local_path:", e
                LOG.error(e)
                return False

DB = _DB()

