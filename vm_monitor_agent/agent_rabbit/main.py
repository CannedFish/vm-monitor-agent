# -*- coding: utf-8 -*-

import settings

if settings.SYSTEM == 'Linux':
    from monitors.linux_monitor import LinuxDirMonitor as DirMonitor
elif settings.SYSTEM == 'Windows':
    from monitors.win_monitor import WinDirMonitor as DirMonitor
else:
    raise ValueError("We are not support %s now." % SYSTEM)

from optparse import OptionParser
import os
import sys
import signal
import time
import logging

logging.basicConfig(level=logging.DEBUG, \
        format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s', \
        datefmt='%m-%d %H:%M', \
        filename=settings.log_file_path, \
        filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

LOG = logging.getLogger(__name__)

from msghandler import MQ_ReceiveService
from auto_uploader import AutoUploader

uploader = None
msg_handler = None
handler_running = True
dir_monitor = None
def exit_handler(signum, frame):
    LOG.debug('Catched interrupt signal')

    global uploader
    uploader.stop()

    global handler_running
    handler_running = False

    global msg_handler
    msg_handler.stop()

    global dir_monitor
    dir_monitor.stop_monitor()

    sys.exit(0)

def main():
    usage = 'Usage: %prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-u', '--uuid', dest='uuid', \
            default=None, \
            help="UUID of this VM")

    options, args = parser.parse_args()
    vm_uuid = options.uuid

    if vm_uuid is None:
        while not os.path.exists(settings.vm_id):
            LOG.warning("vm.id not exists, wait and try again..")
            time.sleep(2)
        with open(settings.vm_id, 'r') as fd:
            vm_uuid = fd.read()

    LOG.info("Agent Rabbit's PID: %s" % os.getpid())
    LOG.info("VM UUID: %s" % vm_uuid)
    # initialization
    try:
        signal.signal(signal.SIGINT, exit_handler)
        if settings.SYSTEM == 'Linux':
            signal.signal(signal.SIGHUP, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)
    except ValueError, e:
        LOG.error(e)

    global dir_monitor
    dir_monitor = DirMonitor(settings.dir_to_be_monitored)
    dir_monitor.start_monitor()

    global uploader
    uploader = AutoUploader(dir_monitor, settings.auto_upload_interval)
    uploader.start()

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
        "rabbitmq.routing_key": vm_uuid or settings.routing_key,
        "rabbitmq.prefetch_count": settings.prefetch_count,
        "rabbitmq.workOrderQueue": vm_uuid or settings.workOrderQueue
    }

    LOG.info("Rabbit Properties: %s" % WORKORDER_RABBITMQ_PROP)

    global msg_handler
    global handler_running
    while handler_running:
        try:
            msg_handler = MQ_ReceiveService(WORKORDER_RABBITMQ_PROP)
            msg_handler.receive_message()
        except Exception, e:
            LOG.error(e)

if __name__ == '__main__':
    main()
