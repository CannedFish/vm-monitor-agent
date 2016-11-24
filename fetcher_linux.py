# -*- coding: utf-8 -*-
# Fetch disk and net data of each process in Linux
import re
import time
from config import settings

class ProcDiskNet(object):
    def __init__(self, pid):
        self._pid = pid
        self._disk_fd = open('/proc/%d/io' % pid)
        self._net_fd = open('/proc/%d/net/dev' % pid)
        self._d_read, self._d_write, self._d_time = self.__get_and_parse_disk()
        self._n_receive, self._n_transmit, self._n_time = self.__get_and_parse_net()
        print "watch %d" % self._pid

    def __del__(self):
        print "unwatch %d" % self._pid
        self._disk_fd.close()
        self._net_fd.close()

    def __get_and_parse_disk(self):
        data = {}
        t = time.time()
        for line in self._disk_fd:
            l = re.split(':', line)
            data[l[0]] = int(l[1])
        self._disk_fd.seek(0)
        # print data
        return data['rchar'], data['wchar'], t

    def __get_and_parse_net(self):
        data = {}
        t = time.time()
        for line in self._net_fd:
            if ':' in line:
                l = re.split(':', line)
                data[l[0].strip()] = map(int, filter(lambda x: x!="", \
                        re.split('\s+', l[1])))
        self._net_fd.seek(0)
        rx, tx = 0, 0
        keys = data.keys()
        for eth in settings['net_interface']:
            if eth in keys:
                rx += data[eth][0]
                tx += data[eth][8]
        # print data
        return rx, tx, t

    @property
    def disk(self):
        d_read, d_write, d_time = self.__get_and_parse_disk()
        r_read = (d_read-self._d_read)/(d_time-self._d_time) # bytes per second
        r_write = (d_write-self._d_write)/(d_time-self._d_time) # bytes per second
        self._d_read, self._d_write, self._d_time = d_read, d_write, d_time
        return round(r_read, 1), round(r_write, 1)

    @property
    def net(self):
        n_receive, n_transmit, n_time = self.__get_and_parse_net()
        r_read = (n_receive-self._n_receive)/(n_time-self._n_time) # bytes per second
        r_write = (n_transmit-self._n_transmit)/(n_time-self._n_time) # bytes per second
        self._n_receive, self._n_transmit, self._n_time = n_receive, n_transmit, n_time
        return round(r_read, 1), round(r_write, 1)

watchedprocs = {}

def watch(pid):
    watchedprocs[pid] = ProcDiskNet(pid)

def unwatch(pid):
    del watchedprocs[pid]

def disk(pid):
    return watchedprocs[pid].disk

def net(pid):
    return watchedprocs[pid].net

