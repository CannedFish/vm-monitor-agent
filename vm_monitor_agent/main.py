# -*- coding: utf-8 -*-
from config import settings
import api_server
import agent
from data_collector import wq
from report_server_api import reporter

if settings['cmd_way'] == 'meta_serv':
    from report_server_api import meta_checker as mc

import sys
import os
import logging
import signal
from subprocess import Popen

# configure log
import logging
from os import path, makedirs

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

log_dir = settings['log_file'].rpartition(settings['log_file'][settings['log_file'].rindex('/')])[0]
if not path.exists(log_dir):
    makedirs(log_dir)

logging.basicConfig(level=log_level[settings['log_level']], \
        format='[%(asctime)s] %(filename)s[line:%(lineno)d]: %(message)s', \
        datefmt='%a, %d %b %Y %H:%M:%S', \
        filename=settings['log_file'], \
        filemode='a')

LOG = logging.getLogger(__name__)

# Agent_Rabbit_Process = None

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

    # global Agent_Rabbit_Process
    # if Agent_Rabbit_Process is not None:
        # os.kill(Agent_Rabbit_PID, signal.SIGTERM)
        # Agent_Rabbit_Process.terminate()

    sys.exit(0)

def main():
    # initialization
    try:
        signal.signal(signal.SIGINT, exit_handler)
        if settings['platform'] == 'Linux':
            signal.signal(signal.SIGHUP, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        LOG.info("Agent PID: %d" % os.getpid())
    except ValueError, e:
        LOG.warning(e)

    # start agent_rabbit
    LOG.info('VM UUID: %s' % settings['instance_id'])
    # p = Popen(['agent_rabbit', '-u', settings['instance_id']], shell=True)
    # Agent_Rabbit_Process = p
    with open(settings['agent_rabbit_app_root'], 'w') as fd:
        fd.write(settings['instance_id'])

    if settings['start_proc_monitor']:
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

    # p.wait()

if __name__ == '__main__':
    main()

