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
        self._stop = None
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
        fetcher.watch(self._pid)

    def __del__(self):
        fetcher.unwatch(self._pid)

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
            LOG.warning('CPU: %d is sent, must between 0 and 100' % val)
        self._cpu = val
        # alert if needed

    @property
    def mem_per(self):
        return self._mem

    @mem_per.setter
    def mem_per(self, val):
        if val > 100 or val < 0:
            LOG.warning('CPU: %d is sent, must between 0 and 100' % val)
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
            LOG.debug(FMT(time.time(), 'Watched', self._pid, self._name))

    def unwatch(self):
        if self._watched:
            self._watched = False
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
            self._stop = time.time()
            if self._watched:
                # send an event
                api.send_report([self.to_dict()], 'proc')
                pass
            LOG.debug(FMT(self._stop, 'Deleted', self._pid, self._name))
        self._status = val

    def basic(self):
        return (self._pid, self._name)

    def complete(self):
        return (self._pid, self._name, self._cpu, \
                self._mem, self._disk, self._net, \
                self._start, self._stop)

    def to_dict(self):
        return {
            'pid': self._pid,
            'cmd': self._name,
            'cpu_util': self._cpu,
            'mem': self._mem,
            'disk_read': self._disk[0],
            'disk_write': self._disk[1],
            'running_time': self._start,
            'shutdown_time': self._stop,
            'net_incoming': self._net[0],
            'net_outgoing': self._net[1]
        }

class Procs(dict):
    def __setitem__(self, key, val):
        if not isinstance(val, Process):
            raise ValueError('Bad value, must be an \
                    instance of Process')
        super(Procs, self).__setitem__(key, val)

    @property
    def alive_num(self):
        return len(filter(lambda x: self[x].status != 'deleted', self.keys()))

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

    @property
    def watched_pids(self):
        return [proc.pid for proc in self._queue]

    def run(self):
        LOG.debug("%s-%d start" % (self.name, self.threadID))
        WatchQueue.__run(self, self._queue, self._delay, self._cond)

    @staticmethod
    def __run(ins, queue, delay, cond):
        while not ins.toExit:
            cond.acquire()
            if len(queue) == 0:
                # hang this thread
                LOG.debug("Watch queue is hanged")
                cond.wait()
            cond.release()
            # send information
            api.send_report([proc.to_dict() for proc in queue], 'proc')
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
    def __init__(self, procs):
        self._procs = procs
        self._cpu = None
        self._mem = None
        self._disk = None
        self._net = None

    @property
    def cpu_per(self):
        return self._cpu

    @cpu_per.setter
    def cpu_per(self, val):
        if val > 100 or val < 0:
            raise ValueError('%d is send, must between 0 and 100' % val)
        self._cpu = val
        # alert if needed

    @property
    def mem_per(self):
        return self._mem

    @mem_per.setter
    def mem_per(self, val):
        if val > 100 or val < 0:
            raise ValueError('%d is send, must between 0 and 100' % val)
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

    def to_dict(self):
        return {
            'cpu_util': self._cpu,
            'mem': self._mem,
            'disk_read': self._disk[0],
            'disk_write': self._disk[1],
            'proc': self._procs.alive_num(),
            'net_incoming': self._net[0],
            'net_outgoing': self._net[1]
        }

# data store
procs = Procs()
vm = VM(procs)
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
        # TODO: append processes exited in this interval
        for pid in procs.keys():
            proc = procs[pid]
            if proc.status in ('created', 'running'):
                ret.append(proc.to_dict())
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

def proc_watched():
    # return watched list
    return wq.watched_pids

# data store api
def update_proc_info(data):
    """
    param data: [(pid, cmd/name, start, %cpu, %mem, diskio, netio)]
    """
    pids = procs.keys()
    # remove deleted prcesses
    # TODO: put these exited processes' info in a cache
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

def get_vm_status():
    return {}

def update_vm_info(data):
    """
    e.g.
    data = {
        'cpu': cpu_percent,
        'mem': mem_percent,
        'disk': (read_bytes, write_bytes)
        'net': (bytes_receive, bytes_sent)
    }
    """
    try:
        vm.cpu_per = data['cpu']
        vm.men_per = data['mem']
        vm.disk_io = data['disk']
        vm.net_io = data['net']
    except ValueError, e:
        LOG.warning(e)

