# -*- coding: utf-8 -*-
import re
from os import path, system

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
    cmd = 'ping -c 2 -w 1 %s'
    import fetcher_linux as fetcher
elif sysstr == 'Windows':
    cmd = 'ping -n 2 -w 1 %s'
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
re = system(cmd % settings['metadata_server_ip'])
if re:
    settings['report_server_ip'] = settings['host_server_ip']
    settings['report_type'] = 'direct'
else:
    settings['report_server_ip'] = settings['metadata_server_ip']
    settings['report_type'] = 'metadata'

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
