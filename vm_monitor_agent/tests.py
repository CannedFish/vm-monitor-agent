# -*- coding: utf-8 -*-
import uuid

import requests, json, time
import sys

from config import  USER, KEY, AUTH_URL, TENANT_NAME, CONTAINER_NAME, UPDATE_CONTAINER_NAME, CONTAINER_NAME_2, OBJECT_NAME_2, OBJECT_NAME, PREAUTH_URL
# api test
def api_test():
    """
    For object storage api testing:
        a. my-container and my-object are first created object for get-container,get object testing, 
           container existing testing and get all objects of container..
           They all get defined in config.py as CONTAINER_NAME and OBJECT_NAME.
        b. we will create a new container("config" + str(uuid.uuid4()) as name) every time for container create testing, 
           update container testing and delete container testing.
        c.
    
    :return: 
    """
    from config import settings
    data = {\
        'method': 'start_monitor',\
        'reserv_id': settings['reserv_id']\
    }
    r = requests.post('http://127.0.0.1:%s/api/cmd' % settings['port'], \
            data='data='+json.dumps(data))


    print "#0 start to authenticate user "
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME
    }
    token = ''
    r = requests.post('http://127.0.0.1:%s/api/authenticate' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    print "result is %s" % return_json
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            token = r['token']
            print "token is %s" %r['token']
    else:
        print "request failed, error is %s"%return_json['msg']


    print "#1 start to get all containers by user \n"
    r = requests.get('http://127.0.0.1:%s/api/containers?preauthtoken=%s&preauthurl=%s&user=%s&tenant_name=%s' %(settings['port'], token,PREAUTH_URL, USER,TENANT_NAME))
    return_json = json.loads(r.content)
    print "results is %s" % return_json


    print "#1 start to get all containers by user \n"
    r = requests.get('http://127.0.0.1:%s/api/containers?user=%s&key=%s&tenant_name=%s&auth_url=%s' %(settings['port'], USER, KEY,TENANT_NAME,AUTH_URL))
    return_json = json.loads(r.content)
    print "results is %s" % return_json
    if return_json['errcode'] ==1:
        print "{:<15}".format("Get container list successfully!")
        for r in return_json['results']:
            print "{:<15}".format("container name is %s \n" %  r['name'])
    else:
        print "{:<15}".format("request failed, error is %s \n"%return_json['msg'])

    print "#2 start to get detect container is existed or not \n"
    r = requests.get('http://127.0.0.1:%s/api/container_exists?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME))
    return_json = json.loads(r.content)
    print "results is %s" % return_json
    if return_json['errcode'] ==1:
        print "{:>15}".format("detect container exists successfully!")
        print "{:>15}".format(return_json['msg'])
    else:
        print "{:>15}".format("request failed, error is %s"%return_json['msg'])

    print "#3 start to get container without data \n"
    r = requests.get('http://127.0.0.1:%s/api/get_container?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME))
    return_json = json.loads(r.content)
    print "result is %s" % return_json
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "container is %s" %r['name']
            print "is_public is %s" %r['is_public']
            print "container_bytes_used is %s" %r['container_bytes_used']
            print "container_object_count is %s" %r['container_object_count']
            print "data is %s" %r['data']
    else:
        print "request failed, error is %s"%return_json['msg']


    print "#4 start to get container with data \n"
    r = requests.get('http://127.0.0.1:%s/api/get_container?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s&with_data=1' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME))
    return_json = json.loads(r.content)
    print "result is %s" % return_json
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "container is %s" %r['name']
            print "is_public is %s" %r['is_public']
            print "container_bytes_used is %s" %r['container_bytes_used']
            print "container_object_count is %s" %r['container_object_count']
            print "data is %s" %r['data']
    else:
        print "request failed, error is %s"%return_json['msg']


    print "#5 start to create container "
    created_container = "config" + str(uuid.uuid4())
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": created_container,
        "metadata": {'is_public': False},
    }

    r = requests.post('http://127.0.0.1:%s/api/create_container' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    print "result is %s" % return_json
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "container is %s" %r['name']
    else:
        print "request failed, error is %s"%return_json['msg']

    print "#6 start to update container for public or private"
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": created_container,
        "metadata": {'is_public': True},
    }
    r = requests.post('http://127.0.0.1:%s/api/update_container' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "container is %s" %r['name']
    else:
        print "request failed, error is %s"%return_json['msg']



    print "#7 start to delete container by container name"
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": created_container,
    }
    r = requests.post('http://127.0.0.1:%s/api/delete_container' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "container is %s" %r['name']
    else:
        print "request failed, error is %s"%return_json['msg']


    # Object api

    print "#8 start to get detect object is existed or not "
    r = requests.get('http://127.0.0.1:%s/api/object_exists?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s&object_name=%s' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME, OBJECT_NAME))
    return_json = json.loads(r.content)
    print "results is" + str(return_json)
    if return_json['errcode'] ==1:
        print return_json['msg']
    else:
        print "request failed, error is %s"%return_json['msg']

    # objects may be file for subdir.So take care of this properly.
    print "#9 start to get all objects of one container by user "
    r = requests.get('http://127.0.0.1:%s/api/objects?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME))
    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            if r.has_key('name'):
                print "object name is %s" % r['name']
            else:
                print " I'm subdir %s" % r['subdir']
    else:
        print "request failed, error is %s"%return_json['msg']


    new_created_object = "object" + str(uuid.uuid4())
    new_created_container = "config"
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "new_container_name": new_created_container,
        "new_object_name": new_created_object,
        "orig_container_name": CONTAINER_NAME,
        "orig_object_name": OBJECT_NAME
    }

    print "#10 start to copy  objects from container to another container "
    r = requests.post('http://127.0.0.1:%s/api/copy_object' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] ==1:
        print "object name is %s" % return_json['msg']
    else:
        print "request failed, error is %s"%return_json['msg']

    print "#11 start to upload object by user "
    object_file = 'test.txt'
    files = {'upload_file': ('test.txt',open("/tmp/test.txt", 'rb'))}
    new_created_object = "object" + str(uuid.uuid4())
    with open('/tmp/test.txt', 'rb') as f:
        data = {
            "user": USER,
            "key": KEY,
            "auth_url": AUTH_URL,
            "tenant_name": TENANT_NAME,
            "container_name": CONTAINER_NAME,
            "object_name": new_created_object,
            "orig_file_name":  f.name,
        }

    #FIXME
    #r = requests.post('http://127.0.0.1:%s/api/upload_object' %(settings['port']), files=files_, data='data='+json.dumps(data))
    headers = {'Content-type': 'multipart/form-data'}

    r = requests.post('http://127.0.0.1:%s/api/upload_object' %(settings['port']), files=files, data=data)
    return_json = json.loads(r.content)
    print  "results is " + str(return_json)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "object name is %s" % r['name']
    else:
        print "request failed, error is %s"%return_json['msg']

    # If path is none,that is create the root dir in the container.Otherwise create subdir in the path
    # Please remind that path is the relative path
    print "#12 start to create a pseudo folder by user in path"
    pseudo_folder_name = "folder" + str(uuid.uuid4())
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": CONTAINER_NAME,
        "pseudo_folder_name": pseudo_folder_name,
        #"path":""
        "path":"folder0de8cdfc-3e4a-4a23-ba82-d182eafda654/"
    }
    r = requests.post('http://127.0.0.1:%s/api/create_pseudo_folder' %(settings['port']), data='data='+json.dumps(data))
    return_json = json.loads(r.content)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "object name is %s" % r['name']
    else:
        print "request failed, error is %s"%return_json['msg']


    print "#13 start to delete container object"
    created_container = "config" + str(uuid.uuid4())
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": new_created_container,
        "object_name": new_created_object,
    }
    r = requests.post('http://127.0.0.1:%s/api/delete_object' % (settings['port']), data='data=' + json.dumps(data))

    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] == 1:
        print "delete object is %s" % return_json['msg']
    else:
        print "request failed, error is %s" % return_json['msg']


    print "#14 start to get container object"
    created_container = "config" + str(uuid.uuid4())
    r = requests.get('http://127.0.0.1:%s/api/get_object?user=%s&key=%s&tenant_name=%s&auth_url=%s&container_name=%s&object_name=%s&with_data=1&download_to=/clouddoc/abc' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL, CONTAINER_NAME, OBJECT_NAME))

    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] == 1:
        print "get object msg is %s" % return_json['msg']
    else:
        print "request failed, error is %s" % return_json['msg']


    print "#15 start to delete container object"
    created_container = "config" + str(uuid.uuid4())
    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": "my-container",
        "object_name": "requirements.txt",
    }
    r = requests.post('http://127.0.0.1:%s/api/delete_object' % (settings['port']), data='data=' + json.dumps(data))

    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] == 1:
        print "delete object is %s" % return_json['msg']
    else:
        print "request failed, error is %s" % return_json['msg']


    print "#17 start to delete container object folder"
    created_container = "config" + str(uuid.uuid4())

    data = {
        "user": USER,
        "key": KEY,
        "auth_url": AUTH_URL,
        "tenant_name": TENANT_NAME,
        "container_name": "my-container",
        "object_name": "folder0de8cdfc-3e4a-4a23-ba82-d182eafda654/folderdea431ac-a553-4b99-8b1d-fc67dc51a0f0/",
    }
    r = requests.post('http://127.0.0.1:%s/api/delete_folder' % (settings['port']), data='data=' + json.dumps(data))

    return_json = json.loads(r.content)
    print "resuls are " + str(return_json)
    if return_json['errcode'] == 1:
        print "msg is %s" % return_json['msg']
    else:
        print "request failed, error is %s" % return_json['msg']

    # NOTE(tsufiev): Ceph backend currently does not support '/info', even
    # some Swift installations do not support it (see `expose_info` docs).
    print "#16 start to get capabilities "
    r = requests.get('http://127.0.0.1:%s/api/get_capabilities?user=%s&key=%s&tenant_name=%s&auth_url=%s' %(settings['port'],USER, KEY,TENANT_NAME,AUTH_URL))
    return_json = json.loads(r.content)
    print "results are " + str(return_json)
    if return_json['errcode'] ==1:
        for r in return_json['results']:
            print "object name is %s" % r['name']
    else:
        print "request failed, error is %s"%return_json['msg']


    return False
    data = {
        'method': 'start_monitor',
        'reserv_id': 'abcde'
    }
    r = requests.post('http://127.0.0.1:%s/api/cmd' % settings['port'], \
            data='data='+json.dumps(data))

    data = {
        'method': 'start_monitor_123',
        'reserv_id': settings['reserv_id']
    }
    r = requests.post('http://127.0.0.1:%s/api/cmd' % settings['port'], \
            data='data='+json.dumps(data))

    time.sleep(18)
    data = {
        'method': 'stop_monitor',
        'reserv_id': settings['reserv_id']
    }
    r = requests.post('http://127.0.0.1:%s/api/cmd' % settings['port'], \
            data='data='+json.dumps(data))

    # r = requests.get('http://127.0.0.1:9999/api/proc/list/0')
    # print "proc list mode 0: \n%s" % r.json()

    # r = requests.get('http://127.0.0.1:9999/api/proc/list/1')
    # print "proc list mode 1: \n%s" % r.json()

    # data = [49, 50]
    # r = requests.post('http://127.0.0.1:9999/api/proc/watch', \
            # data='procs='+json.dumps(data))
    # print "proc watch: %s" % r.json()
    # time.sleep(20)

    # r = requests.post('http://127.0.0.1:9999/api/proc/unwatch', \
            # data='procs='+json.dumps(data))
    # print "proc watch: %s" % r.json()
	
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

    # r = requests.get('http://127.0.0.1:9999/api/proc/list/0')
    # print "proc list mode 0: \n%s" % r.json()

    # r = requests.get('http://127.0.0.1:9999/api/proc/list/1')
    # print "proc list mode 1: \n%s" % r.json()

    # data = [49, 50]
    # r = requests.post('http://127.0.0.1:9999/api/proc/watch', \
            # data='procs='+json.dumps(data))
    # print "proc watch: %s" % r.json()
    # time.sleep(20)

    # r = requests.post('http://127.0.0.1:9999/api/proc/unwatch', \
            # data='procs='+json.dumps(data))
    # print "proc watch: %s" % r.json()
	
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

def reporter_test():
    from report_server_api import reporter

    reporter.start()
    time.sleep(5)
    reporter.pause()
    time.sleep(5)
    reporter.resume()
    time.sleep(5)
    reporter.stop()
    reporter.join()

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
    elif sys.argv[1] == 'report':
        reporter_test()
    else:
        print "bad argument"
        sys.exit(1)

