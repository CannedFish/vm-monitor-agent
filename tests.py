# -*- coding: utf-8 -*-
import requests, json, time
import sys

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
    import data_collector as dc
    
    data = [(i, 'proc'+str(i), time.time(), 0.5, 0.5, 50, 50) for i in xrange(5)]
    dc.update_proc_info(data)
    print "basic:"
    print dc.get_proc_list(0)
    print "complete:"
    print dc.get_proc_list(1)

# test watch queue
def watch_queue_test():
    import data_collector as dc
    
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
    import agent
    
    agent.start()
    time.sleep(5)
    agent.pause()
    time.sleep(5)
    agent.resume()
    time.sleep(5)
    agent.stop()

def agent_linux_test():
    import fetcher_linux as fe
    pid = 55138
    fe.watch(pid)
    time.sleep(1)
    print fe.disk(pid)
    print fe.net(pid)
    fe.unwatch(pid)

def config_test():
    from config import settings
    print settings

if __name__ == '__main__':
    if sys.argv[1] == 'api':
        api_test()
    elif sys.argv[1] == 'dc':
        data_collection_test()
    elif sys.argv[1] == 'wq':
        watch_queue_test()
    elif sys.argv[1] == 'agent':
        agent_test()
    elif sys.argv[1] == 'aglinux':
        agent_linux_test()
    elif sys.argv[1] == 'config':
        config_test()
    else:
        print "bad argument"
        sys.exit(1)

