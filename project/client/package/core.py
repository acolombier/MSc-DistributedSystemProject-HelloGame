import pika
from .model import *
from .serializer import *
from multiprocessing import Queue
from threading import Event

from socket import gaierror

from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication


class GameStartException(Exception):
    def __init__(self, *args):
        super().__init__(*args)    
    
    
class GameCore(QThread):
    eventReceived = pyqtSignal(object)
    statusChanged = pyqtSignal(str)
    errorEncounted = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, nickname, server):
        super().__init__()
        
        self.server, self.player = server, Player(nickname)
        self.isrunning = True
        
        self.isready = Event()
        self.isready.clear()
        
        print ("Initialising a game on %s with the nickname '%s'" % (server, nickname))
        
    def init(self):
        
        self.statusChanged.emit("Connection to server...")
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server))
            
        except gaierror as e:
            self.errorEncounted.emit(str(e))
            return False


        self.channel = self.connection.channel()
        self.replies = Queue()
        
        self.channel.exchange_declare(exchange='broadcast',
                                      exchange_type='fanout')
        bc_queue = self.channel.queue_declare(exclusive=True)
        broadcast_queue_name = bc_queue.method.queue

        self.channel.queue_bind(exchange='broadcast',
                                queue=broadcast_queue_name)

        ### RPC Reply Channel
        reply_to_queue = self.channel.queue_declare(exclusive=True)
        self.callback_queue = reply_to_queue.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
                                   
        ### Main Broadcast Channel
        self.channel.basic_consume(self.on_broadcast,
                                   queue=broadcast_queue_name)
                                
        print("Initialisation completed")
        return True
        
    def register(self):
        self.statusChanged.emit("Accessing to the game...")
        p, self.player.area, self.player.position = self._request(JoinRequest(self.player)).args
        
        assert p.nickname == self.player.nickname
        self.player = p
        
        self.errorEncounted.emit("Connected")
        self.eventReceived.emit(model.Event(model.Event.GAME_READY, self.player))
        
    def on_response(self, ch, method, props, body):
        print("Reply!!!!!")
        data = json_decode(body)
        self.replies.put(data)
        #~ ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def on_broadcast(self, ch, method, props, body):
        data = json_decode(body)
        
        if isinstance(data, model.Event):
            self.eventReceived.emit(data)            
            
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _request(self, payload):
        self.isready.wait()
        assert self.replies.empty()
        self.channel.basic_publish(exchange='',
                                   routing_key='main_queue' if not self.player.is_on_board() else "node_area_%d" % self.player.area,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue
                                         ),
                                   body=json_encode(payload))
    
        print("Waiting...")
        return self.replies.get()
        
    def stop(self):
        self.isrunning = False
        # Todo: wait explicitly for the loop to end up
        
    def run(self):
        if self.init():
            self.isready.set()
            print("Consuming...") 
            while self.isrunning:
                self.connection.process_data_events()
                QCoreApplication.instance().processEvents()
            #~ self.channel.start_consuming()
        self.finished.emit()

