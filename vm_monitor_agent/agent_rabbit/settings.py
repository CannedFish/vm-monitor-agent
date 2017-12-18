# -*- coding: utf-8 -*-

# RabbitMQ
host = "127.0.0.1"
vhost = "/"
username = "guest"
password = "guest"
port = 5672

exchange_name = "htai_file_push"
exchange_type = "topic"
exchange_durable = True
exchange_auto_delete = False

queue_durable = False
queue_auto_delete = False
queue_exclusive = False
routing_key = "VM_UUID*"
prefetch_count = 32
workOrderQueue = "VM_UUID*"

# Auto uploader interval
auto_upload_interval = 10

# Name of this app
from os import path, environ
import platform
import re

# Monitor Directory

SYSTEM = platform.system()
if SYSTEM == 'Linux':
    app_data_root = path.join('/var', 'AgentRabbit')
    conf_dir = path.join('/etc', 'AgentRabbit')
    dir_to_be_monitored = path.join(environ['HOME'], 'clouddoc')
    log_file_path = '/var/log/agent-rabbit.log'
elif SYSTEM == 'Windows':
    app_data_root = path.join(environ['APPDATA'], 'AgentRabbit')
    conf_dir = app_data_root
    dir_to_be_monitored = 'c:\clouddoc'
    log_file_path = path.join(app_data_root, 'agent-rabbit.log')
else:
    raise ValueError("We are not support %s now." % SYSTEM)

db_file_path = path.join(app_data_root, 'msgs.db')
conf_file_path = path.join(conf_dir, 'agent-rabbit.conf')
vm_id = path.join(app_data_root, 'vm.id')

if path.exists(conf_file_path):
    booleanValues = [
        "exchange_durable",
        "exchange_auto_delete",
        "queue_durable",
        "queue_auto_delete",
        "queue_exclusive"
    ]
    intValues = [
        "port",
        "prefetch_count"
    ]
    with open(conf_file_path, 'r') as f:
        conf = globals()
        for line in f:
            if not re.match('\s*#', line) \
                    and not re.match('\s+', line):
                l = re.split('=', line)
                key = l[0].strip()
                if key in booleanValues:
                    conf[key] = bool(l[1].strip())
                elif key in intValues:
                    conf[key] = int(l[1].strip())
                else:
                    conf[key] = l[1].strip()

