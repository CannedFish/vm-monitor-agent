# -*- coding: utf-8 -*-
import time
import psutil
import logging

LOG = logging.getLogger()

from common import MyThread, calc_percent
import data_collector as dc
from config import settings
fetcher = settings['fetcher']

class Agent(MyThread):
    def __init__(self, rr_interval, rt_interval):
        super(Agent, self).__init__('Agent', 1)
        self._delay = rr_interval
        self._rr_interval = rr_interval
        self._rt_interval = rt_interval
        self._disk = self._get_disk_io()
        self._net = self._get_net_io()

    def watch(self):
        self._delay = self._rt_interval

    def unwatch(self):
        self._delay = self._rr_interval

    def work(self):
        dc.update_proc_info(self.fetch_proc_info())
        dc.update_vm_info(self.fetch_vm_info())
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

    def _get_disk_io(self):
        t = time.time()
        io = psutil.disk_io_counters()
        return io.read_bytes, io.write_bytes, t

    def _get_net_io(self):
        t = time.time()
        io = psutil.net_io_counters(pernic=True)
        rx, tx = 0, 0
        nics = io.keys()
        for nic in settings['net_interface']:
            if nic in nics:
                rx += io[nic].bytes_recv
                tx += io[nic].bytes_sent
        return rx, tx, t

    def fetch_vm_info(self):
        disk = self._get_disk_io()
        net = self._get_net_io()
        data = {
            'cpu': psutil.cpu_percent(),
            'mem': psutil.virtual_memory().percent,
            'disk': calc_percent(self._disk, disk),
            'net': calc_percent(self._net, net)
        }
        self._disk = disk
        self._net = net
        return data

    @property
    def delay(self):
        return self._delay

agent = Agent(settings['report_interval'], settings['rt_interval'])

def start():
    agent.start()

def stop():
    agent.stop()
    agent.join()

def pause():
    agent.pause()

def resume():
    agent.resume()

def watch():
    agent.watch()

def unwatch():
    agent.unwatch()

