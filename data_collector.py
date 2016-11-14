from threading import Thread, Condition
import time

# data structure
class Process(object):
    def __init__(self, pid, name, start):
        # property
        self._pid = pid
        self._name = name
        self._start = start
        self._stop = None
        self._cpu = None
        self._mem = None
        self._disk = None
        self._net = None
        # status
        self._watched = False
        self._updated = True
        self._status = 'created' # ('created','running','deleted')

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
    def stop_time(self):
        return self._stop

    @property
    def during_time(self):
        return self._stop - self._start

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
        self._watched = True

    def unwatch(self):
        self._watched = False

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
        if self._watched:
            if self._status in ('created','running') \
                    and val == 'deleted':
                # send an event
                # self._stop = now
                pass
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
            super().__setitem__(key, val)

class WatchQueue(Thread):
    def __init__(self, delay):
        Thread.__init__(self)
        self.threadID = 0
        self.name = 'WatchQueue'
        self._queue = []
        self._delay = delay
        self._cond = Condition()

    def run(self):
        print "%s-%d start" % (self.name, self.threadID)
        WatchQueue.__run(self._queue, self._delay)

    @staticmethod
    def __run(queue, delay):
        while True:
            self._cond.acquire()
            if len(queue) == 0:
                # hang this thread
                print "Watch queue is hanged"
                self._cond.wait()
            self._cond.release()
            # send information
            time.sleep(delay)

    def add(self, procs):
        if not isinstance(procs, list):
            raise ValueError('Bad value, must be a list')
        self._cond.acquire()
        self._queue.extend(procs)
        if len(self._queue) == len(procs):
            # notify the hanged thread
            self._cond.notify()
            print "Watch queue is actived"
        self._cond.release()
        
    def remove(self, procs):
        if not isinstance(procs, list):
            raise ValueError('Bad value, must be a list')
        self._cond.acquire()
        for proc in procs:
            if proc in self._queue:
                self._queue.remove(proc)
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
            ret.append(procs[pid].basic())
    elif mode == 1:
        for pid in procs.keys():
            ret.append(procs[pid].complete())
    return ret

def proc_watch(procs):
    # need all?
    for proc in procs:
        proc.watch()
    wq.add(procs)
    return True

def proc_unwatch(procs):
    # need all?
    for proc in procs:
        proc.unwatch()
    wq.remove(procs)
    return True

def get_vm_status():
    return []

# data store api
def update_proc_basic(data):
    # data from psutil
    pass

def update_proc_disk(data):
    pass

def update_proc_net(data):
    pass

def update_vm_basic(data):
    pass

def update_vm_disk(data):
    pass

def update_vm_net(data):
    pass

