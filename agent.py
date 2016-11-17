from threading import Thread, Condition
import time

import data_collector as dc

class Agent(Thread):
    def __init__(self, delay):
        super(Agent, self).__init__()
        self.threadID = 1
        self.name = 'Agent'
        self._delay = delay

    def run(self):
        print "%s-%d start" % (self.name, self.threadID)
        Agent.__run(self._delay)

    @staticmethod
    def __run(delay):
        pass

def start():
    pass

def stop():
    pass

def pause():
    pass

def resume():
    pass

