# -*- coding: utf-8 -*-
import api_server
import agent
from config import settings

# initialization

# start agent
agent.start()

# start api server
if __name__ == '__main__':
    import sys
    sys.argv.append(settings['port'])
    api_server.run(globals())

