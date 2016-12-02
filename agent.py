# -*- coding: utf-8 -*-
import time
import psutil
import logging

LOG = logging.getLogger()

from common import MyThread
import data_collector as dc
from config import settings
fetcher = settings['fetcher']

class Agent(MyThread):
    def __init__(self, delay):
        super(Agent, self).__init__('Agent', 1)
        self._delay = delay

    def work(self):
        dc.update_proc_info(self.fetch_proc_info())
        time.sleep(self._delay)

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

