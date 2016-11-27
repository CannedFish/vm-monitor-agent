# -*- coding: utf-8 -*-
from threading import Thread, Condition
import time
import psutil

import data_collector as dc
from config import settings
fetcher = settings['fetcher']

class Agent(Thread):
    def __init__(self, delay):
        super(Agent, self).__init__()
        self.threadID = 1
        self.name = 'Agent'
        self._delay = delay
        self._cond = Condition()
        self._exit = False
        self._pause = False

    def run(self):
        print "%s-%d started" % (self.name, self.threadID)
        Agent.__run(self)

    @staticmethod
    def __run(ins):
        while not ins.toExit:
            ins.cond.acquire()
            if ins.toPause:
                ins.cond.wait()
            ins.cond.release()
            dc.update_proc_info(ins.fetch_proc_info())
            time.sleep(ins.delay)

    def fetch_proc_info(self):
        data = []
        for proc in psutil.process_iter():
            info = [proc.pid, proc.name(), \
                    proc.create_time(), \
                    round(proc.cpu_percent(), 1), \
                    round(proc.memory_percent(), 1)]
            info.append(fetcher.disk(proc.pid))
            info.append(fetcher.net(proc.pid))
            data.append(info)

        return data

    @property
    def delay(self):
        return self._delay

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
        print "%s-%d stoped" % (self.name, self.threadID)

    def pause(self):
        self._pause = True
        print "%s-%d paused" % (self.name, self.threadID)

    def resume(self):
        self._pause = False
        self._cond.acquire()
        self._cond.notify()
        self._cond.release()
        print "%s-%d resumed" % (self.name, self.threadID)

agent = Agent(3)

def start():
    agent.start()

def stop():
    agent.stop()
    agent.join()

def pause():
    agent.pause()

def resume():
    agent.resume()

