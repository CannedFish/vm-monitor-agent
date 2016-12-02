# -*- coding: utf-8 -*-
import api_server
import agent
from data_collector import wq
from config import settings
from report_server_api import meta_checker as mc

import sys
import logging
import signal

LOG = logging.getLogger()

# initialization
sys.argv.append(settings['port'])

def handler(signum, frame):
    LOG.debug('Catched interrupt signal')
    agent.stop()
    wq.stop()
    wq.join()
    if settings['report_type'] == 'metadata':
        mc.stop()
        mc.join()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGTERM, handler)

# start agent
agent.start()
wq.start()
if settings['report_type'] == 'metadata':
    mc.start()

# start api server
if __name__ == '__main__':
    api_server.run()

