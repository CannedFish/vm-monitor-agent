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

def exit_handler(signum, frame):
    LOG.debug('Catched interrupt signal')
    agent.stop()
    wq.stop()
    wq.join()
    if settings['report_type'] == 'metadata':
        mc.stop()
        mc.join()
    return 0

def main():
    # initialization
    signal.signal(signal.SIGINT, exit_handler)
    if settings['platform'] == 'Linux':
        signal.signal(signal.SIGHUP, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    # start agent
    agent.start()
    wq.start()
    if settings['report_type'] == 'metadata':
        mc.start()

    # start api server
    if settings['report_type'] == 'direct':
        sys.argv.append(settings['port'])
        sys.argv[1] = settings['port']
        api_server.run()

if __name__ == '__main__':
    main()

