# -*- coding: utf-8 -*-

# RabbitMQ
host = "127.0.0.1"
vhost = "/"
username = "guest"
password = "guest"
port = 5672
exchange_name = "message_router"
exchange_type = "topic"
exchange_durable = True
exchange_auto_delete = False
queue_durable = False
queue_auto_delete = False
queue_exclusive = False
routing_key = "VMS1.*"
prefetch_count = 32
workOrderQueue = "VMS1.workOrderResourceAMQP"

# Log
log_file_path = '/var/log/msghandler.log'

# Name of this app
from os import path, environ
import platform

SYSTEM = platform.system()
if SYSTEM == 'Linux':
    app_data_root = path.join('/var', 'AgentRabbit')
    conf_file_path = path.join('/etc', 'AgentRabbit/agent-rabbit.conf')
elif SYSTEM == 'Windows':
    app_data_root = path.join(environ['APP'], 'AgentRabbit')
    conf_file_path = path.join(environ['APP'], 'AgentRabbit/agent-rabbit.conf')
else:
    raise ValueError("We are not support %s now." % SYSTEM)

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

