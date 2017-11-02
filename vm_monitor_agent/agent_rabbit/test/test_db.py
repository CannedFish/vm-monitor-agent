# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/apple/vm-monitor-agent')

from vm_monitor_agent.agent_rabbit.db import DB

msg = DB.msg("6ee5eb33efad4e45ab46806eac010566", \
        "abcdef0123456789abcdef0123456789")
msg.save()

