#!/usr/bin/env python3
import pika
from package.area import Area
from package import model
import argparse
from multiprocessing import Queue
from threading import Event, Thread, Lock


class DispatchTask:
    def __init__(self, **args):
        self.args = args
        self.ready = None
        self.result = None
        
    def __call__(self, channel):
        self.result = channel.basic_publish(**self.args)
        if self.ready is None:
            self.ready = Event()
        self.ready.set()
        
    def get(self):
        if self.ready is None:
            self.ready = Event()
        self.ready.wait()
        return self.results
        

class Dispatcher(Thread):
    def __init__(self, channel):
        super().__init__()
        self.rmq = Lock()
        self._pending_requests = Queue()
        self.isrunning = True
        self.channel = channel
        
    def __call__(self, **args):
        task = DispatchTask(**args)
        self._pending_requests.put(task)
        return task
        
    def run(self):
        while self.isrunning:
            task = self._pending_requests.get()
            if task is not None:
                try:
                    self.rmq.acquire()
                    task(self.channel)
                finally:
                    self.rmq.release()
        
    def consume(self, connection):        
        while self.isrunning:
            try:
                self.rmq.acquire()
                connection.process_data_events()
            except KeyboardInterrupt:
                self.isrunning = False
            finally:
                self.rmq.release()
        self._pending_requests.put(None)
        self.join()
        
        
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
    
    gameinfo = model.Game(2, 2, 4, 4)
    
    dispatcher = Dispatcher(channel)
    
    area = [Area(i, gameinfo, channel, dispatcher) for i in range(0, 4)]
        
    dispatcher.start()
    dispatcher.consume(connection)
