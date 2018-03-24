import pika
import model
from serializer import *
from multiprocessing import Queue




class GameCore(QThread):
    eventReceived = pyqtSignal(object)
    
    def __init__(self, server, nickname, listener):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=server))

        self.channel = self.connection.channel()
        self.replies = Queue()

        reply_to_queue = self.channel.queue_declare(exclusive=True)
        self.callback_queue = reply_to_queue.method.queue
        
        self.channel.exchange_declare(exchange='broadcast',
                                      exchange_type='fanout')
        bc_queue = channel.queue_declare(exclusive=True)
        broadcast_queue_name = bc_queue.method.queue

        self.channel.queue_bind(exchange='broadcast',
                                queue=broadcast_queue_name)

        ### RPC Reply Channel
        self.channel.basic_consume(self.on_response,
                                   queue=self.callback_queue)
                                   
        ### Main Broadcast Channel
        self.channel.basic_consume(self.on_broadcast,
                                   queue=queue_name)
                                   
        self.player = Player(nickname)
        self.listener = listener

    def on_response(self, ch, method, props, body):
        data = json_decode(body)
        self.put(data)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    def on_broadcast(self, ch, method, props, body):
        data = json_decode(body)
        
        if isinstance(data, model.Event):
            self.eventReceived.emit(data)            
            
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _request(self, payload):
        # ToDo: some basic cs
        assert self.replies.count() == 0
        self.channel.basic_publish(exchange='direct',
                                   routing_key='main_queue' if not self.player.is_on_board() else "node_area_%d" % self.player.area,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue
                                         ),
                                   body=json_encode(payload))

        return self.replie.get()
        
    def run(self):
        self.channel.start_consuming()

