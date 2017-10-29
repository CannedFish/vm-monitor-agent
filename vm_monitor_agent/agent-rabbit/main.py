# -*- coding: utf-8 -*-

from mqhandler import MQ_ReceiveService
import settings

import logging

logging.basicConfig(level=logging.DEBUG, \
        format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s', \
        datefmt='%m-%d %H:%M', \
        filename=settings.log_file_path, \
        filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

LOG = logging.getLogger(__name__)

def main():
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
        "rabbitmq.routing_key": settings.routing_key,
        "rabbitmq.prefetch_count": settings.prefetch_count,
        "rabbitmq.workOrderQueue": settings.workOrderQueue
    }
    
    while True:
        try:
            h = MQ_ReceiveService(WORKORDER_RABBITMQ_PROP, thread_pool_size)
            h.receive_message()
        except Exception, e:
            LOG.error(e)

if __name__ == '__main__':
    main()

