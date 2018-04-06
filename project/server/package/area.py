import pika
from . import model
from .serializer import *
from random import randint
import uuid
from time import time
from threading import Timer
from copy import copy

class Area:
    def __init__(self, _id, channel):
        self.id = _id
        
        self.players = {}
        
        self.channel = channel
        
        channel.queue_declare(queue='main_queue')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_request, queue='main_queue')
    
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
        
        self.player_alive_check() 

    def player_alive_check(self):
        # Make a local copy of the current state, in case of someone arrives during the cleaning routing (RuntimeError)
        players = copy(self.players)
        
        for pos, player in players.items():
            if player.last_activity + 6 < time():
                self.player_disconnect(player, model.Player.DISCONNECT_TIMEOUT)
        
        self.player_ka_timer = Timer(6.0, self.player_alive_check)
        self.player_ka_timer.start() 
        
    def player_disconnect(self, player, r=model.Player.DISCONNECT_QUIT):        
        del self.players[player.position]        
        self.channel.basic_publish(exchange='broadcast',
                         routing_key='',
                         body=json_encode(model.Event(model.Event.QUIT, player=player, reason=r)))

    def on_request(self, ch, method, props, body):
        data = json_decode(body)
                
        print("On request: %s" % body)
        
        if hasattr(data, 'player') and data.player.uuid in self.players.keys():
            self.players[data.player].last_activity = time()
        
        if isinstance(data, model.MoveRequest):
            # Destination is away, we forward the request
            if data.area() != self.id:
                ch.basic_publish(exchange='direct',
                                 routing_key='node_area_%d.*' % data.area,
                                 properties=pika.BasicProperties(reply_to = props.reply_to),
                                 body=body)
            else:                
                if data.player not in self.players.values():
                    print("Error, unknown player")
                    
                # Destination is free, we accept the move
                elif data.cellid() not in self.players.keys():
                    self.players[data.cellid()] = data.player
                    self.players[data.cellid()].last_activity = time()
                    
                    ch.basic_publish(exchange='broadcast',
                                     routing_key='',
                                     body=json_encode(model.Event(model.Event.PLAYER_MOVE, data.player, data.destination)))
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
            while c in self.players.keys():
                c = randint(0, 15)
                
            print("Accepting new client '%s' at pos %s" % (data.player.nickname, c))
                
            data.player.area = self.id
            data.player.position = c
            data.player.uuid = str(uuid.uuid4())
            self.players[c] = data.player
            self.players[c].last_activity = time()
            
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             body=json_encode(
                                model.Event(model.Event.PLAYER_JOIN, 
                                            player=data.player, 
                                            area=self.id, 
                                            position=c)))
            
            ch.basic_publish(exchange='broadcast',
                             routing_key='',
                             body=json_encode(
                                model.Event(model.Event.PLAYER_JOIN, 
                                            player=data.player)))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.Event):
            if data.type == model.Event.QUIT and data.player in self.players.values():
                self.player_disconnect(data.player, model.Player.DISCONNECT_QUIT)
            if data.type == model.Event.KEEP_ALIVE and data.player in self.players.values() \
                and self.players[data.player.position] == data.player:
                self.players[data.player.position].last_activity = time()
                
            ch.basic_ack(delivery_tag = method.delivery_tag)

    def run(self):
        self.channel.start_consuming()
