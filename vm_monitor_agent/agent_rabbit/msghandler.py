# -*- coding: utf-8 -*-

import logging
import pika
import sys
import json

# import cloud_api
from message import Message

LOG = logging.getLogger(__name__)

class MQ_Send_Service(object):
    def __init__(self, mqconfig):
        self.mqconfig = mqconfig
        self.mqhost = mqconfig["rabbitmq.host"]
        self.mqVhost = mqconfig["rabbitmq.vhost"]
        self.mqUser = mqconfig["rabbitmq.username"]
        self.mqPasswd = mqconfig["rabbitmq.password"]
        self.msgQueue = mqconfig["rabbitmq.workOrderQueue"]
        self.queueDurable = mqconfig["rabbitmq.queue_durable"]
        self.queueAutoDelete = mqconfig["rabbitmq.queue_auto_delete"]
        self.queueExclusive = mqconfig["rabbitmq.queue_exclusive"]
        self.port = mqconfig["rabbitmq.port"]
        self.exchange = mqconfig["rabbitmq.exchange_name"]
        self.exchangeType = mqconfig["rabbitmq.exchange_type"]
        self.exchangeDurable = mqconfig["rabbitmq.exchange_durable"]
        self.exchangeAutoDelete = mqconfig["rabbitmq.exchange_auto_delete"]
        self.routingkey = mqconfig["rabbitmq.routing_key"]

        self.credentials = pika.PlainCredentials(self.mqUser, self.mqPasswd)
        self.parameters = pika.ConnectionParameters(self.mqhost, \
                self.port, self.mqVhost, self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)

    def send_message(self, msgBody):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.exchange, \
                                type=self.exchangeType, \
                                durable=self.exchangeDurable, \
                                auto_delete=self.exchangeAutoDelete)
        channel.basic_publish(routing_key=self.routingkey, \
                exchange=self.exchange, body=msgBody)
        LOG.info("Sent %r" % msgBody)
        channel.close()

class MQ_ReceiveService(object):
    def __init__(self, mqconfig):
        self.mqconfig = mqconfig
        self.mqhost = mqconfig["rabbitmq.host"]
        self.mqVhost = mqconfig["rabbitmq.vhost"]
        self.mqUser = mqconfig["rabbitmq.username"]
        self.mqPasswd = mqconfig["rabbitmq.password"]
        self.msgQueue = mqconfig["rabbitmq.workOrderQueue"]
        self.queueDurable = mqconfig["rabbitmq.queue_durable"]
        self.queueAutoDelete = mqconfig["rabbitmq.queue_auto_delete"]
        self.queueExclusive = mqconfig["rabbitmq.queue_exclusive"]
        self.port = mqconfig["rabbitmq.port"]
        self.exchange = mqconfig["rabbitmq.exchange_name"]
        self.exchangeType = mqconfig["rabbitmq.exchange_type"]
        self.exchangeDurable = mqconfig["rabbitmq.exchange_durable"]
        self.exchangeAutoDelete = mqconfig["rabbitmq.exchange_auto_delete"]
        self.routingkey = mqconfig["rabbitmq.routing_key"]

        self.credentials = pika.PlainCredentials(self.mqUser, self.mqPasswd)
        self.parameters = pika.ConnectionParameters(self.mqhost, \
                                                    self.port, \
                                                    self.mqVhost, \
                                                    self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)

    def receive_message(self):
        channel = self.connection.channel()
        self._channel = channel
        channel.exchange_declare(exchange=self.exchange, \
                                type=self.exchangeType, \
                                durable=self.exchangeDurable, \
                                auto_delete=self.exchangeAutoDelete)
        channel.queue_declare(queue=self.msgQueue, \
                            durable=self.queueDurable, \
                            exclusive=self.queueExclusive, \
                            auto_delete=self.queueAutoDelete)
        channel.queue_bind(exchange=self.exchange, \
                queue=self.msgQueue, \
                routing_key=self.routingkey)

        def callback(ch, method, properties, body):
            # print " [x] %r:%r" % (method.routing_key, body)
            LOG.info('Message received: %s' % body)
            msg = json.loads(body)

            # Persistence
            LOG.info("Save received message to disk: %s." % msg)
            msg_obj = Message(msg)
            if not msg_obj.save():
                LOG.warning("Save failed.")
                return ;

            # Download file
            LOG.info("Try to download %s/%s, orig_name is %s, type is %s" \
                    % (msg['container_id'], msg['object_id'], \
                    msg['orig_name'], msg['content_type']))
            if not msg_obj.file_download():
                LOG.warning("Download failed.")
                return ;

        self._tag = channel.basic_consume(callback, queue=self.msgQueue, no_ack=True)
        channel.start_consuming()

    def stop(self):
        self._channel.stop_consuming()
        self._channel.basic_cancel(self._tag)
        self._channel.close()
