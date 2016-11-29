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

settings['fetcher'] = fetcher

cmd = 'ping -n 2 -w 1 %s'
re = system(cmd % settings['metadata_server_ip'])
if re:
    settings['report_server_ip'] = settings['host_server_ip']
else:
    settings['report_server_ip'] = settings['metadata_server_ip']
