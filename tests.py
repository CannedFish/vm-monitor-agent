# -*- coding: utf-8 -*-
import requests, json, time
import sys

# api test
def api_test():
    r = requests.get('http://127.0.0.1:9999/api/proc/list/0')
    print "proc list mode 0: \n%s" % r.json()

    r = requests.get('http://127.0.0.1:9999/api/proc/list/1')
    print "proc list mode 1: \n%s" % r.json()

    data = [49, 50]
    r = requests.post('http://127.0.0.1:9999/api/proc/watch', \
            data='procs='+json.dumps(data))
    print "proc watch: %s" % r.json()
    time.sleep(20)

    r = requests.post('http://127.0.0.1:9999/api/proc/unwatch', \
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
            for i in [1, 2, 3, 5]]
    dc.update_proc_info(data)
    time.sleep(2)
    print "\nwatch all"
    pids = [p[0] for p in data]
    dc.proc_watch(pids)
    time.sleep(16)
    print "\nupdate proc info, again"
    data = [(i, 'proc'+str(i), time.time(), 0.5, 0.5, 50, 50) \
            for i in (5, 7, 8, 9)]
    dc.update_proc_info(data)
    print dc.get_proc_list(0)
    dc.proc_watch([3, 5, 7])
    time.sleep(8)
    print "\nunwatch all"
    dc.proc_unwatch([5, 7, 8, 9])

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
    pid = 0
    fe.watch(pid)
    time.sleep(1)
    print fe.disk(pid)
    print fe.net(pid)
    fe.unwatch(pid)
    
def agent_win_test():
    import fetcher_win as fe
    pid = 4
    fe.watch(pid)
    time.sleep(1)
    print fe.disk(pid)
    print fe.net(pid)
    fe.unwatch(pid)
	
def wmi_test():
	from config import settings
	import wmi
	c = wmi.WMI()
	wql = "SELECT * FROM Win32_LogicalDisk"
	for disk in c.query(wql):
		print disk

def config_test():
    from config import settings
    print settings

def log_test():
    from config import settings
    import logging
    LOG = logging.getLogger()
    LOG.debug("Log start")
    LOG.debug("Log end")

def metadata_checker_test():
    from report_server_api import meta_checker as mc
    
    mc.start()
    time.sleep(5)
    mc.pause()
    time.sleep(5)
    mc.resume()
    time.sleep(5)
    mc.stop()
    mc.join()

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
    elif sys.argv[1] == 'agwin':
        agent_win_test()
    elif sys.argv[1] == 'config':
        config_test()
    elif sys.argv[1] == 'wmi':
		wmi_test()
    elif sys.argv[1] == 'log':
        log_test()
    elif sys.argv[1] == 'meta':
        metadata_checker_test()
    else:
        print "bad argument"
        sys.exit(1)

