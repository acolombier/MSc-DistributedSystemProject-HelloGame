import pika
from .model import *
from .serializer import *
from multiprocessing import Queue

from socket import gaierror

from PyQt5.QtCore import QThread, pyqtSignal


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
        
        print ("Initialising a game on %s with the nickname '%s'" % (server, nickname))
        
    def init(self):
        
        self.statusChanged.emit("Connection to server...")
        try:
            print("Connection started...")
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server))
            print("Connection done")
            
        except gaierror as e:
            self.errorEncounted.emit(str(e))
            return False


        self.channel = self.connection.channel()
        self.replies = Queue()

        reply_to_queue = self.channel.queue_declare(exclusive=True)
        self.callback_queue = reply_to_queue.method.queue
        
        self.channel.exchange_declare(exchange='broadcast',
                                      exchange_type='fanout')
        bc_queue = self.channel.queue_declare(exclusive=True)
        broadcast_queue_name = bc_queue.method.queue

        self.channel.queue_bind(exchange='broadcast',
                                queue=broadcast_queue_name)

        ### RPC Reply Channel
        self.channel.basic_consume(self.on_response,
                                   queue=self.callback_queue)
                                   
        ### Main Broadcast Channel
        self.channel.basic_consume(self.on_broadcast,
                                   queue=broadcast_queue_name)
                                
        
        print("Connection request")
        self.statusChanged.emit("Accessing to the game...")
        self.player.area, self.player.position = self._request(JoinRequest(self.player))
        self.errorEncounted.emit("Connected")
        self.eventReceived.emit(Event(GAME_READY, self.player))
        return True
        
        

    def on_response(self, ch, method, props, body):
        data = json_decode(body)
        self.replies.put(data)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def on_broadcast(self, ch, method, props, body):
        data = json_decode(body)
        
        if isinstance(data, model.Event):
            self.eventReceived.emit(data)            
            
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _request(self, payload):
        # ToDo: some basic cs
        assert self.replies.empty()
        self.channel.basic_publish(exchange='direct',
                                   routing_key='main_queue' if not self.player.is_on_board() else "node_area_%d" % self.player.area,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue
                                         ),
                                   body=json_encode(payload))

        return self.replies.get()
        
    def run(self):
        if self.init():
            self.channel.start_consuming()
        self.finished.emit()

