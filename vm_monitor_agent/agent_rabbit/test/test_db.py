# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/apple/vm-monitor-agent')

from vm_monitor_agent.agent_rabbit.db import DB

msg = DB.msg("6ee5eb33efad4e45ab46806eac010566", \
        "abcdef0123456789abcdef0123456789")
if not msg.save():
    print "message save failed"

docpath = '/home/someone/clouddoc'
if not msg.update_local_path(docpath):
    print "update local_path failed"

print "get_ids_by_localpath:", DB.get_ids_by_localpath(docpath)

print "1) get info: %s" % DB.get_info()
DB.info(
    "username",
    "password",
    "http://192.168.1.48:5000/v2.0",
    "tenant",
    "6677ddef0123456789abcdef0123456789"
)
print "2) get info: %s" % DB.get_info()

