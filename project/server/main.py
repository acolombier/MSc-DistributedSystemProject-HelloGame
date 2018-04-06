#!/usr/bin/env python3
import pika
from package.area import Area
import argparse
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hello Game server launcher.')
    
    parser.add_argument('--single-node', dest='node_id', default=1, type=int, nargs='?', help='Launch a single node with the given id')
    parser.add_argument('rmq_host', type=str, default='localhost',
                help='Server name that run RabbitMQ')
    parser.add_argument('width', type=int, default=2,
                help='Number of Area on a row')
    parser.add_argument('height', type=int, default=2,
                help='Number of Area on a col')
    args = parser.parse_args()
    
    

    connection = pika.BlockingConnection(pika.ConnectionParameters(args.rmq_host))
    channel = connection.channel()
    
    
    if (args.node_id == -1):
        [Area(i, channel) for i in range(0, 4)][0].run()
    else:
        Area(args.node_id, channel).run()
