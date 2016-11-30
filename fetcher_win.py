# -*- coding: utf-8 -*-
# Fetch disk and net data of each process in Windows
import psutil
import time

class ProcIO(object):
    def __init__(self, pid):
        self._pid = pid
        self._io = self.__get_io()
		
    @property
    def pid(self):
        return self._pid

    @property
    def io(self):
        stat = self.__get_io()
        dur = stat[2]-self._io[2]
        if dur == 0:
            return (0, 0)
        r_bps = round((stat[0]-self._io[0])/dur, 1)
        w_bps = round((stat[1]-self._io[1])/dur, 1)
        self._io = stat
        return (r_bps, w_bps)
		
    def __get_io(self):
        now = time.time()
        if hasattr(self, '_io') and now == self._io[2]:
            return self._io

        try:
            proc = psutil.Process(self._pid)
            pinfo = proc.as_dict(ad_value='')
        except psutil.NoSuchProcess as err:
            unwatch(self._pid)
            return self._io

        iostat = pinfo['io_counters']
        data = {}
        for k, v in zip(iostat._fields, iostat):
            data[k] = v

        return data['read_bytes'], data['write_bytes'], now
		
proc_io_list = {}

def watch(pid):
    if not pid in proc_io_list.keys():
        proc = ProcIO(pid)
        proc_io_list[pid] = proc
        print 'watch %d' % pid

def unwatch(pid):
    if pid in proc_io_list.keys():
        del proc_io_list[pid]
        print 'unwatch %d' % pid

def disk(pid):
    if pid in proc_io_list.keys():
        return proc_io_list[pid].io
    return (0, 0)

def net(pid):
    if pid in proc_io_list.keys():
        return proc_io_list[pid].io
    return (0, 0)

