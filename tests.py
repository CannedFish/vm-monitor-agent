import requests, json, time
import sys

import data_collector as dc
import agent

# api test
def api_test():
    r = requests.get('http://0.0.0.0:9999/api/proc/list/0')
    print "proc list mode 0: %s" % r.json()

    r = requests.get('http://0.0.0.0:9999/api/proc/list/1')
    print "proc list mode 1: %s" % r.json()

    data = [0, 1, 2, 3, 4]
    r = requests.post('http://0.0.0.0:9999/api/proc/watch', \
            data='procs='+json.dumps(data))
    print "proc watch: %s" % r.json()

    r = requests.post('http://0.0.0.0:9999/api/proc/unwatch', \
            data='procs='+json.dumps(data))
    print "proc watch: %s" % r.json()

# test data collection
def data_collection_test():
    data = [(i, 'proc'+str(i), time.time(), 0.5, 0.5, 50, 50) for i in xrange(5)]
    dc.update_proc_info(data)
    print "basic:"
    print dc.get_proc_list(0)
    print "complete:"
    print dc.get_proc_list(1)

# test watch queue
def watch_queue_test():
    time.sleep(1)
    print "\nempty queue"
    time.sleep(3)
    print "\nupdate proc info"
    data = [(i, 'proc'+str(i), time.time(), 0.5, 0.5, 50, 50) \
            for i in xrange(5)]
    dc.update_proc_info(data)
    time.sleep(2)
    print "\nwatch all"
    pids = [p[0] for p in data]
    dc.proc_watch(pids)
    time.sleep(16)
    print "\nupdate proc info, again"
    data = [(i, 'proc'+str(i), time.time(), 0.5, 0.5, 50, 50) \
            for i in xrange(3, 7)]
    dc.update_proc_info(data)
    print dc.get_proc_list(0)
    dc.proc_watch(range(3, 6))
    time.sleep(8)
    print "\nunwatch all"
    dc.proc_unwatch(range(0, 6))

def agent_test():
    agent.start()
    time.sleep(5)
    agent.pause()
    time.sleep(5)
    agent.resume()
    time.sleep(5)
    agent.stop()

if __name__ == '__main__':
    if sys.argv[1] == 'api':
        api_test()
    elif sys.argv[1] == 'dc':
        data_collection_test()
    elif sys.argv[1] == 'wq':
        watch_queue_test()
    elif sys.argv[1] == 'agent':
        agent_test()
    else:
        print "bad argument"
        sys.exit(1)

