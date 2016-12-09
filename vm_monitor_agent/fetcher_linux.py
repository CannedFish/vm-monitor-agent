# -*- coding: utf-8 -*-
# Fetch disk and net data of each process in Linux
import re
import time
from config import settings
from common import calc_percent

class ProcDiskNet(object):
    def __init__(self, pid):
        self._pid = pid
        # self._disk_fd = open('/proc/%d/io' % pid)
        # self._net_fd = open('/proc/%d/net/dev' % pid)
        self._d_read, self._d_write, self._d_time = self.__get_and_parse_disk()
        self._n_receive, self._n_transmit, self._n_time = self.__get_and_parse_net()
        # print "watch %d" % self._pid

    # def __del__(self):
        # print "unwatch %d" % self._pid
        # self._disk_fd.close()
        # self._net_fd.close()

    def __get_and_parse_disk(self):
        data = {}
        t = time.time()
        try:
            with open('/proc/%d/io' % self._pid) as fd:
                for line in fd:
                    l = re.split(':', line)
                    data[l[0]] = int(l[1])
            # self._disk_fd.seek(0)
        except IOError, e:
            return (self._d_read, self._d_write, self._d_time) \
                    if hasattr(self, '_d_read') else (0, 0, t)
        return data['rchar'], data['wchar'], t

    def __get_and_parse_net(self):
        data = {}
        t = time.time()
        try:
            with open('/proc/%d/net/dev' % self._pid) as fd:
                for line in fd:
                    if ':' in line:
                        l = re.split(':', line)
                        data[l[0].strip()] = map(int, filter(lambda x: x!="", \
                                re.split('\s+', l[1])))
            # self._net_fd.seek(0)
        except IOError, e:
            return (self._n_receive, self._n_transmit, self._n_time) \
                    if hasattr(self, '_n_receive') else (0, 0, t)
        rx, tx = 0, 0
        keys = data.keys()
        for eth in settings['net_interface']:
            if eth in keys:
                rx += data[eth][0]
                tx += data[eth][8]
        return rx, tx, t

    @property
    def disk(self):
        d_read, d_write, d_time = self.__get_and_parse_disk()
        r_read, r_write = calc_percent((self._d_read, self._d_write, self._d_time), \
                (d_read, d_write, d_time))
        self._d_read, self._d_write, self._d_time = \
                d_read, d_write, d_time
        return r_read, r_write

    @property
    def net(self):
        n_receive, n_transmit, n_time = self.__get_and_parse_net()
        r_read, r_write = calc_percent(\
                (self._n_receive, self._n_transmit, self._n_time), \
                (n_receive, n_transmit, n_time))
        self._n_receive, self._n_transmit, self._n_time = \
                n_receive, n_transmit, n_time
        return r_read, r_write

watchedprocs = {}

def watch(pid):
    watchedprocs[pid] = ProcDiskNet(pid)

def unwatch(pid):
    del watchedprocs[pid]

def disk(pid):
    if pid in watchedprocs.keys():
        return watchedprocs[pid].disk
    return (0, 0)

def net(pid):
    if pid in watchedprocs.keys():
        return watchedprocs[pid].net
    return (0, 0)

