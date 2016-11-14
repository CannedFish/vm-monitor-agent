import api_server
import data_collector as dc # for test
import time # for test

# initialization
# for test
for i in xrange(5):
    proc = dc.Process(i, 'init-%d' % i, time.time())
    dc.procs[proc.pid] = proc

# start agent

# start api server
if __name__ == '__main__':
    api_server.run(globals())

