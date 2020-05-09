"""Messaging via RabbitMQ."""
import json
import pika
import time
import uuid

import crontris
from .settings import Config

def connect_rabbit(tries=10):
    try:
        rabbit_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=Config.RABBIT_HOST))
    except pika.exceptions.AMQPConnectionError:
        if tries > 0:
            time.sleep(2)
            rabbit_connection = connect_rabbit(tries - 1)
        else:
            raise
    return rabbit_connection

connection = connect_rabbit()

class Listener():
    def __init__(self):
        self.channel = connection.channel()
        self.channel.queue_declare(queue='scheduling', durable=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='scheduling', on_message_callback=self.schedule)

    def start(self):
        self.channel.start_consuming()

    def schedule(self, ch, method, props, body):
        response = crontris.scheduler.consume(json.loads(body))
        if response is not None:
            ch.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(correlation_id=props.correlation_id),
                body=json.dumps(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)


class RpcClient():
    def __init__(self):
        self.channel = connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(n))
        while self.response is None:
            connection.process_data_events()
        return self.response
