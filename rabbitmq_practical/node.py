#!/usr/bin/env python3
import sys
import pika
from threading import Thread
from random import randint


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

class Node(Thread):
    IN = 0
    OUT = 1
    def __init__(self, n, total_node):
        super().__init__()
        self.id = n
        self.total_node = total_node
        self.channel = channel.queue_declare(queue='node_%d' % self.id, exclusive=True)
        channel.queue_declare(queue='node_%d' % ((self.id - 1) % total_node), exclusive=True)
        
        channel.basic_consume(self.receiver,
                          queue='node_%d' % ((self.id - 1) % self.total_node))  
                           
                           
    #~ def run(self):
        #~ print("binding node %d to %d" % (self.id, (self.id - 1) % self.total_node))
          
        #~ print("Starting node %d" % self.id)
        
    def receiver(self, ch, method, properties, body):
        
        if body.endswith(b"|%d" % self.id):
            print("[Node %d] %s" % (self.id, body))
        else:
            self.send(body)
        
        ch.basic_ack(delivery_tag = method.delivery_tag)
    
    def send(self, body):
        channel.basic_publish(exchange='',
                  routing_key=self.channel.method.queue,
                  body=(b"%d:" % self.id) + body)


nodes = []

for i in range(0, 5):
    nodes.append(Node(i, 5))
    
#~ for n in nodes:
    #~ n.start()
        
nodes[randint(0, 4)].send(b"test|%d" % randint(0, 4))

channel.start_consuming()
        
