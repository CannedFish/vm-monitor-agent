#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import logging
import pika
import json

# sys.path.append('/var/www/msghandler')
from vm_monitor_agent.agent_rabbit import settings
from vm_monitor_agent.agent_rabbit.msghandler import MQ_Send_Service

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename='myapp.log',
        filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

LOG = logging.getLogger(__name__)

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    # parser.add_option('-f', '--file', dest='filename', \
            # help="Give message sample file", metavar='FILE')
    options, args = parser.parse_args()
    # if len(args) < 1:
        # print "Usage: test_send_msg $msg_file_path"
        # sys.exit(1)
    # filepath = args[0]

    WORKORDER_RABBITMQ_PROP = {
        "rabbitmq.host": settings.host,
        "rabbitmq.vhost": settings.vhost,
        "rabbitmq.username": settings.username,
        "rabbitmq.password": settings.password,
        "rabbitmq.port": settings.port,
        "rabbitmq.exchange_name": settings.exchange_name,
        "rabbitmq.exchange_type": settings.exchange_type,
        "rabbitmq.exchange_durable": settings.exchange_durable,
        "rabbitmq.exchange_auto_delete": settings.exchange_auto_delete,
        "rabbitmq.queue_durable": settings.queue_durable,
        "rabbitmq.queue_auto_delete": settings.queue_auto_delete,
        "rabbitmq.queue_exclusive": settings.queue_exclusive,
        "rabbitmq.routing_key": "this-is-not-a-uuid",
        "rabbitmq.prefetch_count": settings.prefetch_count,
        "rabbitmq.workOrderQueue": "this-is-not-a-uuid"
    }

    LOG.info(json.dumps(WORKORDER_RABBITMQ_PROP))

    # send message
    mq_sender = MQ_Send_Service(WORKORDER_RABBITMQ_PROP)
    info = {
        "uuid": "abcdkeasjfk-sajdfwjf203",
        "container_id": "test",
        "object_id": "down-20180204050909.xlsx",
        "username": "yes",
        "password": "123",
        "auth_url": "http://192.168.1.52:5000/v2.0",
        "tenant_name": "yes",
        "orig_name": "down.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    mq_sender.send_message(json.dumps(info))
    LOG.info("send msg %s", info)
    print "finish send mq"

if __name__ == '__main__':
    main()

