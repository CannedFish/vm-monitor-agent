# -*- coding: utf-8 -*-
import api_server
import agent
from config import settings

import sys

# initialization
sys.argv.append(settings['port'])

# start agent
agent.start()

# start api server
if __name__ == '__main__':
    api_server.run()

