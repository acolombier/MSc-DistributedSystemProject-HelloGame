import pika
from . import model
from .serializer import *
from random import randint
import uuid
from time import time
from threading import Timer
from copy import copy

class Area:
    def __init__(self, _id, gameinfo, channel, disp):
        self.id = _id
        
        self.players = {}
        
        self.gameinfo = gameinfo
        
        self.channel = channel
        self.dispatcher = disp

        # TODO : I added the attribute area_dimension like this, 
            #can you add it the the init function
        self.area_dimension = 4
        
        channel.queue_declare(queue='main_queue')
        channel.queue_declare(queue='node_area_%d' % self.id)
        channel.basic_qos(prefetch_count=1)
    
        ### Declaring Broadcast
        channel.exchange_declare(exchange='broadcast',
                                 exchange_type='fanout')                                 
        channel.queue_bind(exchange='broadcast',
                           queue="main_queue")
                                 
        ### Declaring Direct exchange for already registered 
        channel.exchange_declare(exchange='direct',
                                 exchange_type='topic')
        channel.queue_bind(exchange='direct',
                           routing_key='node_area_%d' % self.id,
                           queue='node_area_%d' % self.id)
                                 
        ### Declaring Direct exchange for not registered 
        channel.exchange_declare(exchange='public_direct',
                                 exchange_type='topic')
        channel.queue_bind(exchange='public_direct',
                           queue="main_queue",
                           routing_key='main_queue')
                           
        channel.basic_consume(self.on_request, queue='main_queue')        
        channel.basic_consume(self.on_request, queue='node_area_%d' % self.id)
        
        self.player_alive_check() 
        
        print("Node %d is up" % self.id)

    # TODO check this
    def say_hello(self, player):
        ch.basic_publish(exchange='broadcast',
                         routing_key='',
                         body=json_encode(model.Event(model.Event.PLAYER_SAYS, player=player, message='Hello')))

    def player_alive_check(self):
        # Make a local copy of the current state, in case of someone arrives during the cleaning routing (RuntimeError)
        players = copy(self.players)
        
        for pos, player in players.items():
            if player.last_activity + 6 < time():
                self.player_disconnect(player, model.Player.DISCONNECT_TIMEOUT)
        
        self.player_ka_timer = Timer(6.0, self.player_alive_check)
        self.player_ka_timer.start() 
        
    def player_disconnect(self, player, r=model.Player.DISCONNECT_QUIT):        
        if player.position in self.players.keys():
            del self.players[player.position]        
            self.dispatcher(exchange='broadcast',
                            routing_key='',
                            body=json_encode(model.Event(model.Event.QUIT, player=player, reason=r)))

    def on_request(self, ch, method, props, body):
        data = json_decode(body)
                
        print("Area %d: On request: %s" % (self.id, body))
        
        if hasattr(data, 'player') and data.player.uuid in self.players.keys():
            self.players[data.player].last_activity = time()
        
        if isinstance(data, model.MoveRequest):
            # Destination is away, we forward the request
            if data.area() != self.id:
                self.dispatcher(exchange='direct',
                                routing_key='node_area_%d' % data.area(),
                                properties=pika.BasicProperties(reply_to = props.reply_to),
                                body=body)
            else:                
                if data.cellid() not in self.players.keys():
                    data.player.area = self.id
                    data.player.position = data.cellid()
                    self.players[data.cellid()] = data.player
                    self.players[data.cellid()].last_activity = time()
                    
                    self.dispatcher(exchange='broadcast',
                                    routing_key='',
                                    body=json_encode(model.Event(model.Event.PLAYER_MOVE, player=data.player, area=self.id, position=data.cellid())))
                    
                    # TODO : Send hello to a player in the same area
                    for cell in (data.cellid()-1, data.cellid()+1, data.cellid()-size,data.cellid()+size):
                        if cell in self.players.keys():
                            say_hello(data.player)


                else:
                    data.status = model.MoveRequest.FAILED
                    self.dispatcher(exchange='direct',
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
            
            self.dispatcher(exchange='',
                            routing_key=props.reply_to,
                            body=json_encode(self.gameinfo.playercopy(player)))
            
            self.dispatcher(exchange='broadcast',
                            routing_key='',
                            body=json_encode(
                            model.Event(model.Event.PLAYER_JOIN, 
                                        player=data.player)))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.Event):
            if data.type == model.Event.QUIT and data.player in self.players.values():
                self.player_disconnect(data.player, model.Player.DISCONNECT_QUIT)
            elif data.type == model.Event.KEEP_ALIVE and data.player in self.players.values() \
                and data.player.position in self.players.keys() \
                and self.players[data.player.position] == data.player:
                self.players[data.player.position].last_activity = time()                
            elif data.type == model.Event.PLAYER_MOVE and data.player in self.players.values() \
                and data.area != self.id:
                    del self.players[list(self.players.keys())[list(self.players.values()).index(data.player)]]     
            elif data.type == model.Event.PLAYER_JOIN:
                self.dispatcher(model.Event(model.Event.GAME_INFO, players=list(self.players.values())))
            
            # TODO check this
            if data.type == model.Event.PLAYER_MOVE:
                topology_dim = 4
                # data.args.destination.area I don't think it works like this
                if data.args.area + topology_dim == self.id:
                    y = self.area_dimension - 1
                    for x in range(self.area_dimension):
                        if (y*self.area_dimension + x) in self.players.keys():
                            say_hello(player)
                elif data.args.area - topology_dim == self.id:
                    y = 0
                    for x in range(self.area_dimension):
                        if (y*self.area_dimension + x) in self.players.keys():
                            say_hello(player)
                elif data.args.area - 1 == self.id:
                    x = self.area_dimension - 1
                    for y in range(self.area_dimension):
                        if (y*self.area_dimension + x) in self.players.keys():
                            say_hello(player)
                elif data.args.area - 1 == self.id:
                    x = 0
                    for y in range(self.area_dimension):
                        if (y*self.area_dimension + x) in self.players.keys():
                            say_hello(player)

            #TODO
            #if data.type == model.Event.PLAYER_SAYS:
    
            ch.basic_ack(delivery_tag = method.delivery_tag)
