# -*- coding: utf-8 -*-
from config import settings
import api_server
import agent
from data_collector import wq
from report_server_api import reporter
from vm_monitor_agent.agent_rabbit import main as agent_rabbit_main

if settings['cmd_way'] == 'meta_serv':
    from report_server_api import meta_checker as mc

import sys
import os
import logging
import signal
from multiprocessing import Process

LOG = logging.getLogger(__name__)

Agent_Rabbit_Process = None

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

    global Agent_Rabbit_Process
    # os.kill(Agent_Rabbit_PID, signal.SIGTERM)
    Agent_Rabbit_Process.terminate()

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
    
    # start agent
    agent.start()
    wq.start()
    reporter.start()
    if settings['cmd_way'] == 'meta_serv':
        mc.start()

    # start agent_rabbit
    p = Process(target=agent_rabbit_main, name="AgentRabbit", \
            args=(settings['instance_id'], ))
    p.start()
    Agent_Rabbit_Process = p

    # start api server
    if settings['cmd_way'] == 'rest':
        sys.argv.append(settings['port'])
        sys.argv[1] = settings['port']
        api_server.run()

    p.join()

if __name__ == '__main__':
    main()

