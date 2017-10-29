#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import logging
import pika
import json

# sys.path.append('/var/www/msghandler')
from msghandler import settings
from msghandler.mqhandler import MQ_Send_Service

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
    if len(args) < 1:
        print "Usage: test_send_msg $msg_file_path"
        sys.exit(1)
    filepath = args[0]

    LOG.info(json.dumps(settings.WORKORDER_RABBITMQ_PROP))

    # send message
    mq_sender = MQ_Send_Service(settings.WORKORDER_RABBITMQ_PROP)
    with open(filepath, 'r') as fd:
        info = json.loads(fd.read())
        mq_sender.send_message(json.dumps(info))
        LOG.info("send msg %s", info)
        print "finish send mq"

if __name__ == '__main__':
    # if len(sys.argv) < 2:
        # print "Usage: test_send_msg $msg_file_path"
        # sys.exit(1)

    main()

