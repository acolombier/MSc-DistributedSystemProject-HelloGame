import pika
from . import model
from .serializer import *
from random import randint


class Area:
    def __init__(self, _id, channel):
        self.id = _id
        
        self.players = {}
        
        self.channel = channel
        
        #~ channel.queue_declare(queue='connect')
        channel.queue_declare(queue='main_queue')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_request, queue='main_queue')
        #~ channel.basic_consume(self.on_request, queue='connect')
    
        ### Declaring Broadcast
        channel.exchange_declare(exchange='broadcast',
                                 exchange_type='fanout')                                 
        channel.queue_bind(exchange='broadcast',
                           queue="main_queue")
                                 
        ### Declaring Direct exchange for already registered 
        channel.exchange_declare(exchange='direct',
                                 exchange_type='topic')
        channel.queue_bind(exchange='direct',
                           queue="main_queue",
                           routing_key='node_area_%d.*' % self.id)
        channel.queue_bind(exchange='direct',
                           queue="main_queue",
                           routing_key='main_queue')


    def on_request(self, ch, method, props, body):
        data = json_decode(body)
        
        if isinstance(data, model.MoveRequest):
            if data.player not in self.players.keys():
                print("Error, unknown player")
                return
                
            if data.area() != self.id:
                ch.basic_publish(exchange='direct',
                                 routing_key='node_area_%d.*' % data.area,
                                 properties=pika.BasicProperties(reply_to = props.reply_to),
                                 body=body)
            else:
                if data.cellid() not in self.players.values():
                    self.players[data.player] = data.cellid()
                    
                    ch.basic_publish(exchange='broadcast',
                                     body=json_encode(Event(Event.PLAYER_MOVE, data.player, data.destination)))
                    # TODO: say hi if some is nearby
                else:
                    data.status = model.MoveRequest.FAILED
                    ch.basic_publish(exchange='direct',
                                     routing_key=props.reply_to,
                                     body=json_encode(data))
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.JoinRequest):
            if len(self.players) == 16:
                print("Error: the area is full")
                ch.basic_nack(delivery_tag = method.delivery_tag)
                
            c = randint(0, 15)
            while c in self.players.values():
                c = randint(0, 15)
                
            print("Accepting new client '%s' at pos %s" % (data.player.nickname, c))
                
            self.players[data.player] = c
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             body=json_encode(model.Event(model.Event.PLAYER_JOIN, data.player, self.id, c)))
            # TODO: say hi if some is nearby
            
            ch.basic_ack(delivery_tag = method.delivery_tag)

    def run(self):
        self.channel.start_consuming()
