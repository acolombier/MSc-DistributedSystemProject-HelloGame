import pika
from . import model
from .serializer import *
from random import randint
import uuid
from time import time
from threading import Timer
from copy import copy
from random import choice

class Area:    
                    
    AVAILABLE_COLOR = [13, #	Dark red (#800000)
                       14, #	Dark green (#008000)
                       15, #	Dark blue (#000080)
                       10, #	Cyan (#00ffff)
                       16, #	Dark cyan (#008080)
                       11, #	Magenta (#ff00ff)
                       7,  #	Dark magenta (#800080)
                       12, #	Yellow (#ffff00)
                       18, #	Dark yellow (#808000)
                       5,  #	Gray (#a0a0a4)
                       4,  #	Dark gray (#808080)
                       6]  #    Light gray (#c0c0c0) 
                       
    def __init__(self, _id, gameinfo, channel, disp):
        self.id = _id
        
        self.players = {}
        
        
        gameinfo.area_color[_id] = choice(Area.AVAILABLE_COLOR)
        self.gameinfo = gameinfo
        
        self.channel = channel
        self.dispatcher = disp
        
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
        
        print("Node %d(color %d) is up" % (self.id, gameinfo.area_color[_id]))

    def player_alive_check(self):
        # Make a local copy of the current state, in case of someone arrives during the cleaning routing (RuntimeError)
        players = copy(self.players)
        
        for pos, player in players.items():
            if player.last_activity + 10 < time():
                self.player_disconnect(player, model.Player.DISCONNECT_TIMEOUT)
        
        self.player_ka_timer = Timer(15.0, self.player_alive_check)
        self.player_ka_timer.start() 
        
    def player_disconnect(self, player, r=model.Player.DISCONNECT_QUIT):        
        if player.position in self.players.keys():
            del self.players[player.position]        
            self.dispatcher(exchange='broadcast',
                            routing_key='',
                            body=json_encode(model.Event(model.Event.QUIT, player=player, reason=r)))

    def on_request(self, ch, method, props, body):
        data = json_decode(body)
                
        # ~ print("Area %d: On request: %s" % (self.id, body))
        
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
                    data.status = model.MoveRequest.SUCCESS
                    
                    self.players[data.cellid()] = data.player
                    self.players[data.cellid()].last_activity = time()                    
            
                    self.dispatcher(exchange='',
                                    routing_key=props.reply_to,
                                    body=json_encode(data))
                            
                    self.dispatcher(exchange='broadcast',
                                    routing_key='',
                                    body=json_encode(model.Event(model.Event.PLAYER_MOVE, 
                                                                 player=data.player, 
                                                                 area=self.id, 
                                                                 position=data.cellid())))
                else:
                    data.status = model.MoveRequest.FAILED
                    self.dispatcher(exchange='',
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
                            body=json_encode(self.gameinfo.playercopy(data.player)))
            
            self.dispatcher(exchange='broadcast',
                            routing_key='',
                            body=json_encode(
                            model.Event(model.Event.PLAYER_JOIN, 
                                        player=data.player)))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.Event):
            if data.type == model.Event.QUIT and data.player in self.players.values():
                self.player_disconnect(data.player, model.Player.DISCONNECT_QUIT)
            elif data.type == model.Event.KEEP_ALIVE and data.player.area == self.id \
                and data.player.position in self.players.keys() \
                and self.players[data.player.position] == data.player:
                self.players[data.player.position].last_activity = time()    
            elif data.type == model.Event.PLAYER_MOVE:  
                # TODO check this
                topology_dim = 4
                if data.player.area == self.id:
                    if (data.player.position - 1) in self.players.keys():                        
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[data.player.position - 1], msg=model.Hello.generate(data.player.nickname))))
                    if (data.player.position + 1) in self.players.keys():                        
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[data.player.position + 1], msg=model.Hello.generate(data.player.nickname))))
                    if (data.player.position - self.gameinfo.sxarea) in self.players.keys():                        
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[data.player.position - self.gameinfo.sxarea], msg=model.Hello.generate(data.player.nickname))))
                    
                    if (data.player.position + self.gameinfo.sxarea) in self.players.keys():                        
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[data.player.position + self.gameinfo.sxarea], msg=model.Hello.generate(data.player.nickname))))
                        
                    # ~ print("%d ?%d: x neightboor " % (self.id, data.player.area), abs(data.player.area - self.id) == 1 and int(data.player.area / self.gameinfo.nxarea) == int(self.id / self.gameinfo.nxarea))
                    # ~ print("%d ?%d: y neightboor " % (self.id, data.player.area), abs(data.player.area - self.id) == self.gameinfo.nxarea and data.player.area % self.gameinfo.nxarea == self.id % self.gameinfo.nxarea)
                 
                    # ~ data.player.position / self.gameinfo.nxarea == self.gameinfo.nyarea - 1
                # data.destination.area I don't think it works like this
                # ~ if data.area + topology_dim == self.id:
                    # ~ y = self.area_dimension - 1
                    # ~ for x in range(self.area_dimension):
                        # ~ if (y*self.area_dimension + x) in self.players.keys():
                            # ~ send_hello(data.destination.area, player)
                # ~ elif data.area - topology_dim == self.id:
                    # ~ y = 0
                    # ~ for x in range(self.area_dimension):
                        # ~ if (y*self.area_dimension + x) in self.players.keys():
                            # ~ send_hello(data.destination.area, player)
                # ~ elif data.area - 1 == self.id:
                    # ~ x = self.area_dimension - 1
                    # ~ for y in range(self.area_dimension):
                        # ~ if (y*self.area_dimension + x) in self.players.keys():
                            # ~ send_hello(data.destination.area, player)
                # ~ elif data.area - 1 == self.id:
                    # ~ x = 0
                    # ~ for y in range(self.area_dimension):
                        # ~ if (y*self.area_dimension + x) in self.players.keys():
                            # ~ send_hello(data.destination.area, player)   
                # end check
                 
                if data.player in self.players.values() and data.area != self.id:
                    del self.players[list(self.players.keys())[list(self.players.values()).index(data.player)]]      
            elif data.type == model.Event.PLAYER_JOIN:
                self.dispatcher(exchange='broadcast',
                                routing_key='',
                                body=json_encode(
                                model.Event(model.Event.GAME_INFO, players=list(self.players.values()))))
                
            ch.basic_ack(delivery_tag = method.delivery_tag)

    def stop(self):
        self.player_ka_timer.cancel()
