# -*- coding: utf-8 -*-
import re
import uuid
from os import path, environ

CONFIG_PATH = ['etc/vma.conf', '/etc/vma.conf']

settings = {'start_proc_monitor':True}

for p in CONFIG_PATH:
    if not path.exists(p):
        continue
    with open(p) as f:
        for line in f:
            if not re.match('\s*#', line) \
                and not re.match('\s+', line):
                l = re.split('=', line)
                settings[l[0].strip()] = l[1].strip()
    settings['net_interface'] = map(lambda x: x.strip(), \
            re.split(',', settings['net_interface']))
    settings['start_proc_monitor'] = True if settings['start_proc_monitor'] == 'true' else False

# configure platform specific
import platform
sysstr = platform.system()
if sysstr == 'Linux':
    # app_data_root = path.join('/var', 'AgentRabbit')
    import fetcher_linux as fetcher
elif sysstr == 'Windows':
    # app_data_root = path.join(environ['APPDATA'], 'AgentRabbit')
    import fetcher_win as fetcher
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raise ValueError('Platform not support, only Linux and Windows')
settings['platform'] = sysstr

USER = "yes"
KEY = "123"
AUTH_URL = "http://192.168.1.89:5000/v2.0"
PREAUTH_URL = 'http://192.168.1.7:7480/swift/v1'
#PREAUTH_URL = 'http://192.168.1.7:5000/v2.0'
TENANT_NAME = "yes"
CONTAINER_NAME = "dongdong"
UPDATE_CONTAINER_NAME = "update_config" + str(uuid.uuid4())
OBJECT_NAME = "my-object"

CONTAINER_NAME_2 = "config2"
OBJECT_NAME_2 = "object2"
# configure fetcher
settings['fetcher'] = fetcher

# configure report server
# get instance_id && reserv_id && report_delay from metadata server
from common import do_get
settings['host_server_ip'] = 'http://localhost:8086/wsgi_app.py'
ret = do_get(settings['metadata_server_ip'] + 'chargesystem_url/')
if ret['success']:
    settings['host_server_ip'] = ret['data']
ret = do_get(settings['metadata_server_ip'] + 'instance-id/')
settings['instance_id'] = "this-is-not-a-uuid"
if ret['success']:
    settings['instance_id'] = ret['data']
ret = do_get(settings['metadata_server_ip'] + 'issued_token/')
settings['reserv_id'] = 'MWRiOqvtztyRFSVIqFzTgNreIhkRFnUb'
if ret['success']:
    settings['reserv_id'] = ret['data']
ret = do_get(settings['metadata_server_ip'] + 'poll_interval/')
settings['report_interval'] = 10
if ret['success'] and re.match('^[\d\.]+$', str(ret['data'])):
    settings['report_interval'] = ret['data']
print settings['report_interval']
settings['rt_interval'] = int(settings['rt_interval'])

# settings['agent_rabbit_app_root'] = path.join(app_data_root, 'vm.id')

