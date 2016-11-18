import api_server
import agent

# initialization

# start agent
agent.start()

# start api server
if __name__ == '__main__':
    api_server.run(globals())

