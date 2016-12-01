# -*- coding: utf-8 -*-
from threading import Thread, Condition
import time
import logging

LOG = logging.getLogger()

import report_server_api as api
from config import settings
fetcher = settings['fetcher']

def FMT(now, event, pid, name):
    return '[%s] %10s, %6d, %s' \
            % (time.asctime(time.localtime(now)), \
            event, pid, name)

# data structure
class Process(object):
    def __init__(self, pid, name, start):
        # property
        self._pid = pid
        self._name = name
        self._start = start
        self._last_update = start
        self._cpu = None
        self._mem = None
        self._disk = None # (r, w)
        self._net = None # (r, t)
        # status
        self._watched = False
        self._updated = True
        self._status = 'created' # ('created','running','deleted')
        LOG.debug(FMT(start, 'Created', pid, name))

    def __str__(self):
        return "(%d,%s,%f,%f,%s,%s)" % (self._pid, self._name, \
                self._cpu, self._mem, self._disk, self._net)

    @property
    def pid(self):
        return self._pid

    @property
    def name(self):
        return self._name

    @property
    def start_time(self):
        return self._start

    @property
    def update_time(self):
        return self._last_update

    @update_time.setter
    def update_time(self, val):
        if val < self._last_update:
            raise ValueError('Bad value, must bigger than last')
        self._last_update = val

    @property
    def during_time(self):
        return self._last_update - self._start

    @property
    def cpu_per(self):
        return self._cpu

    @cpu_per.setter
    def cpu_per(self, val):
        if val > 100 or val < 0:
            if self._pid == 0:
                val = round(val/10.0, 1)
            else:
                raise ValueError('Bad value, must between 0 and 100')
        self._cpu = val
        # alert if needed

    @property
    def mem_per(self):
        return self._mem

    @mem_per.setter
    def mem_per(self, val):
        if val > 100 or val < 0:
            raise ValueError('Bad value, must between 0 and 100')
        self._mem = val
        # alert if needed

    @property
    def disk_io(self):
        return self._disk

    @disk_io.setter
    def disk_io(self, val):
        self._disk = val
        # alert if needed

    @property
    def net_io(self):
        return self._net

    @net_io.setter
    def net_io(self, val):
        self._net = val
        # alert if needed

    def watch(self):
        if not self._watched:
            self._watched = True
            fetcher.watch(self._pid)
            LOG.debug(FMT(time.time(), 'Watched', self._pid, self._name))

    def unwatch(self):
        if self._watched:
            self._watched = False
            fetcher.unwatch(self._pid)
            LOG.debug(FMT(time.time(), 'Unwatched', self._pid, self._name))

    @property
    def updated(self):
        return self._updated

    @updated.setter
    def updated(self, val):
        self._updated = val

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val):
        if val not in ('created','running','deleted'):
            raise ValueError('Bad value, must be \
                    created, running or deleted')
        if self._status in ('created','running') \
                and val == 'deleted':
            stop = time.time()
            if self._watched:
                # send an event
                pass
            LOG.debug(FMT(stop, 'Deleted', self._pid, self._name))
        self._status = val

    def basic(self):
        return (self._pid, self._name)

    def complete(self):
        return (self._pid, self._name, self._cpu, \
                self._mem, self._disk, self._net)

class Procs(dict):
    def __setitem__(self, key, val):
        if not isinstance(val, Process):
            raise ValueError('Bad value, must be an \
                    instance of Process')
        super(Procs, self).__setitem__(key, val)

class WatchQueue(Thread):
    def __init__(self, delay):
        super(WatchQueue, self).__init__()
        self.threadID = 0
        self.name = 'WatchQueue'
        self._queue = []
        self._delay = delay
        self._cond = Condition()
        self._exit = False

    @property
    def toExit(self):
        return self._exit

    def run(self):
        LOG.debug("%s-%d start" % (self.name, self.threadID))
        # print "%s-%d start" % (self.name, self.threadID)
        WatchQueue.__run(self, self._queue, self._delay, self._cond)

    @staticmethod
    def __run(ins, queue, delay, cond):
        while not ins.toExit:
            cond.acquire()
            if len(queue) == 0:
                # hang this thread
                LOG.debug("Watch queue is hanged")
                # print "Watch queue is hanged"
                cond.wait()
            cond.release()
            # send information
            api.send_report([proc.complete() for proc in queue])
            time.sleep(delay)
        LOG.debug("%s-%d stoped" % (ins.name, ins.threadID))

    def add(self, procs):
        if not isinstance(procs, list):
            raise ValueError('Bad value, must be a list')
        self._cond.acquire()
        for proc in procs:
            if not proc in self._queue:
                self._queue.append(proc)
        if len(self._queue) == len(procs):
            # notify the hanged thread
            self._cond.notify()
            LOG.debug("Watch queue is actived")
            # print "Watch queue is actived"
        self._cond.release()
        
    def remove(self, procs):
        if not isinstance(procs, list):
            raise ValueError('Bad value, must be a list')
        self._cond.acquire()
        for proc in procs:
            if proc in self._queue:
                self._queue.remove(proc)
        self._cond.release()

    def stop(self):
        self._exit = True
        if len(self._queue) == 0:
            self._cond.acquire()
            self._cond.notify()
            self._cond.release()

class VM(object):
    def __init__(self):
        self._cpu = None
        self._mem = None
        self._disk = None
        self._net = None

    @property
    def cpu_per(self):
        return self._cpu

    @cpu_per.setter
    def cpu_per(self, val):
        if val > 1 or val < 0:
            raise ValueError('Bad value, must between 0 and 1')
        self._cpu = val
        # alert if needed

    @property
    def mem_per(self):
        return self._mem

    @mem_per.setter
    def mem_per(self, val):
        if val > 1 or val < 0:
            raise ValueError('Bad value, must between 0 and 1')
        self._mem = val
        # alert if needed

    @property
    def disk_per(self):
        return self._disk

    @disk_per.setter
    def disk_per(self, val):
        if val > 1 or val < 0:
            raise ValueError('Bad value, must between 0 and 1')
        self._disk = val
        # alert if needed

    @property
    def net_per(self):
        return self._net

    @net_per.setter
    def net_per(self, val):
        if val > 1 or val < 0:
            raise ValueError('Bad value, must between 0 and 1')
        self._net = val
        # alert if needed

# data store
procs = Procs()
vm = VM()
wq = WatchQueue(3)

# data fetch api
def get_proc_list(mode):
    ret = []
    if mode == 0:
        for pid in procs.keys():
            proc = procs[pid]
            if proc.status in ('created', 'running'):
                ret.append(proc.basic())
    elif mode == 1:
        for pid in procs.keys():
            proc = procs[pid]
            if proc.status in ('created', 'running'):
                ret.append(proc.complete())
    return ret

def proc_watch(pids):
    # need all?
    wps = []
    for pid in pids:
        proc = procs[pid]
        proc.watch()
        wps.append(proc)
    wq.add(wps)
    return True

def proc_unwatch(pids):
    # need all?
    wps = []
    for pid in pids:
        proc = procs[pid]
        proc.unwatch()
        wps.append(proc)
    wq.remove(wps)
    return True

def get_vm_status():
    return []

# data store api
def update_proc_info(data):
    """
    param data: [(pid, cmd/name, start, %cpu, %mem, diskio, netio)]
    """
    pids = procs.keys()
    for pid in pids:
        if procs[pid].status == 'deleted':
            del procs[pid]
        else:
            procs[pid].updated = False
    pids = procs.keys()
    for pid, name, start_time, cpu, mem, disk, net in data:
        if not pid in pids:
            procs[pid] = Process(pid, name, start_time)
        proc = procs[pid]
        proc.cpu_per = cpu
        proc.mem_per = mem
        proc.disk_io = disk
        proc.net_io = net
        proc.status = 'running'
        proc.updated = True
    # handle deleted processes
    now = time.time()
    d_procs = []
    for pid in pids:
        # import pdb
        # pdb.set_trace()
        if not procs[pid].updated:
            procs[pid].status = 'deleted'
            procs[pid].update_time = now
            d_procs.append(pid)
    if len(d_procs) > 0:
        proc_unwatch(d_procs)
        # TODO: remove deleted prcesses

def update_vm_basic(data):
    pass

def update_vm_disk(data):
    pass

def update_vm_net(data):
    pass

