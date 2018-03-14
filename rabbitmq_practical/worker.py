#!/usr/bin/env python3
import pika
import time


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)
    
if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')
    
    channel.basic_consume(callback,
                      queue='hello')
    channel.basic_qos(prefetch_count=1)

    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
