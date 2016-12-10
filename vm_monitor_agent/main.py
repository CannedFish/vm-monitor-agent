# -*- coding: utf-8 -*-
import api_server
import agent
from data_collector import wq
from config import settings
from report_server_api import reporter

if settings['cmd_way'] == 'meta_serv':
    from report_server_api import meta_checker as mc

import sys
import logging
import signal

LOG = logging.getLogger()

def exit_handler(signum, frame):
    LOG.debug('Catched interrupt signal')
    agent.stop()
    
    reporter.stop()
    reporter.join()

    if settings['cmd_way'] == 'meta_serv':
        mc.stop()
        mc.join()
    
    wq.stop()
    wq.join()
    
    if settings['platform'] == 'Linux':
        sys.exit(0)

def main():
    # initialization
    try:
        signal.signal(signal.SIGINT, exit_handler)
        if settings['platform'] == 'Linux':
            signal.signal(signal.SIGHUP, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)
    except ValueError, e:
        LOG.warning(e)
    
    # start agent
    agent.start()
    wq.start()
    reporter.start()
    if settings['cmd_way'] == 'meta_serv':
        mc.start()

    # start api server
    if settings['cmd_way'] == 'rest':
        sys.argv.append(settings['port'])
        sys.argv[1] = settings['port']
        api_server.run()

if __name__ == '__main__':
    main()

