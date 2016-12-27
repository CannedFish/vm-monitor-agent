# -*- coding: utf-8 -*-
import re
from os import path

CONFIG_PATH = ['etc/vma.conf', '/etc/vma.conf']

settings = {}

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

# configure platform specific
import platform
sysstr = platform.system()
if sysstr == 'Linux':
    import fetcher_linux as fetcher
elif sysstr == 'Windows':
    import fetcher_win as fetcher
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raise ValueError('Platform not support, only Linux and Windows')
settings['platform'] = sysstr

# configure fetcher
settings['fetcher'] = fetcher

# configure report server
# get instance_id && reserv_id && report_delay from metadata server
from common import do_get
settings['host_server_ip'] = 'http://localhost:8086/wsgi_app.py'
re = do_get(settings['metadata_server_ip'] + 'chargesystem_url/')
if re['success']:
    settings['host_server_ip'] = re['data']
re = do_get(settings['metadata_server_ip'] + 'instance-id/')
settings['instance_id'] = None
if re['success']:
    settings['instance_id'] = re['data']
re = do_get(settings['metadata_server_ip'] + 'issued_token/')
settings['reserv_id'] = 'MWRiOqvtztyRFSVIqFzTgNreIhkRFnUb'
if re['success']:
    settings['reserv_id'] = re['data']
re = do_get(settings['metadata_server_ip'] + 'poll_interval/')
settings['report_interval'] = 10
if re['success'] and re.match('^[\d\.]+$', re['data']):
    settings['report_interval'] = re['data']
print settings['report_intervaL']
settings['rt_interval'] = int(settings['rt_interval'])

# configure log
import logging
from os import path, makedirs

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

log_dir = settings['log_file'].rpartition(settings['log_file'][settings['log_file'].rindex('/')])[0]
if not path.exists(log_dir):
    makedirs(log_dir)

logging.basicConfig(level=log_level[settings['log_level']], \
        format='[%(asctime)s] %(filename)s[line:%(lineno)d]: %(message)s', \
        datefmt='%a, %d %b %Y %H:%M:%S', \
        filename=settings['log_file'], \
        filemode='a')

