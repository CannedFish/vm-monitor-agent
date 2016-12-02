# -*- coding: utf-8 -*-
from threading import Thread, Condition
import logging

LOG = logging.getLogger()

class MyThread(Thread):
    def __init__(self, name, tid):
        super(MyThread, self).__init__()
        self.threadID = tid
        self.name = name
        self._cond = Condition()
        self._exit = False
        self._pause = False

    def run(self):
        LOG.debug("%s-%d started" % (self.name, self.threadID))
        while not self._exit:
            self._cond.acquire()
            if self._pause:
                self._cond.wait()
            self._cond.release()
            self.work()
    
    @property
    def cond(self):
        return self._cond

    @property
    def toExit(self):
        return self._exit

    @property
    def toPause(self):
        return self._pause

    def stop(self):
        self._exit = True
        LOG.debug("%s-%d stoped" % (self.name, self.threadID))

    def pause(self):
        self._pause = True
        LOG.debug("%s-%d paused" % (self.name, self.threadID))

    def resume(self):
        self._pause = False
        self._cond.acquire()
        self._cond.notify()
        self._cond.release()
        LOG.debug("%s-%d resumed" % (self.name, self.threadID))

