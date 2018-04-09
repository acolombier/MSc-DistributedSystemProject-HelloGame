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
                       #5,  #	Gray (#a0a0a4) <Doesn't look good>
                       #4,  #	Dark gray (#808080)  <Doesn't look good>
                       #6  #    Light gray (#c0c0c0) <Doesn't look good>
                       ]
                       
    def __init__(self, _id, gameinfo, channel, disp):
        self.id = _id
        
        self.players = {}
        
        
        gameinfo.area_color[_id] = choice(Area.AVAILABLE_COLOR)
        self.gameinfo = gameinfo
        
        self.channel = channel
        self.dispatcher = disp

        print (self.gameinfo)
        # TODO : keep list of free cells to remove the overhead when of looping until finding free cell 
        # There is an easy way

        # TODO : I added the attribute area_dimension like this, 
        # use self.gameinfo.n[x|y]area instead

        channel.queue_declare(queue='main_queue')         
        channel.queue_declare(queue='node_area_%d' % self.id)
        channel.basic_qos(prefetch_count=1)
    
        ### Declaring Broadcast
        channel.exchange_declare(exchange='broadcast',
                                 exchange_type='fanout')                           
        channel.queue_bind(exchange='broadcast',
                           queue="main_queue")
        bcast_channel = channel.queue_declare(exclusive=True)
        bcast_channel_name = bcast_channel.method.queue

        channel.queue_bind(exchange='broadcast',
                           queue=bcast_channel_name)

                                 
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
         
        # Binding consumer
        channel.basic_consume(self.on_request, queue='main_queue')          
        channel.basic_consume(self.on_request, queue=bcast_channel_name)          
        channel.basic_consume(self.on_request, queue='node_area_%d' % self.id)
        
        self.player_alive_check() 
        
        print("Node %d is up" % self.id)

    def player_alive_check(self):
        # Make a local copy of the current state, in case of someone arrives during the cleaning routing (RuntimeError)
        players = copy(self.players)
        
        for pos, player in players.items():
            if player.last_activity + model.Game.KEEP_ALIVE_TIMEOUT < time():
                self.player_disconnect(player, model.Player.DISCONNECT_TIMEOUT)
                print("Player %s has timed out from area %d" % (player.nickname, self.id))
        
        self.player_ka_timer = Timer(model.Game.KEEP_ALIVE_TIMEOUT + model.Game.GRACE_TIME, self.player_alive_check)
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

        # save the last activity for a player connected
        if hasattr(data, 'player') and data.player.uuid in self.players.keys():
            self.players[data.player].last_activity = time()
        
        # Check request type and handle it depending on its type  
        if isinstance(data, model.MoveRequest):
            # Destination is in another area, forward the request to that area
            if data.area() != self.id:
                self.dispatcher(exchange='direct',
                                routing_key='node_area_%d' % data.area(),
                                properties=pika.BasicProperties(reply_to = props.reply_to),
                                body=body)
            # Destination in my this area
            else:
                # Check if the destination cell is not occupied by other players
                if data.cellid() not in self.players.keys():
                    if data.player.position in self.players.keys() and self.players[data.player.position] == data.player:
                        del self.players[data.player.position]
                    
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
			# TODO : Say Hello if there is a player in adjacent cell
			# Has to be done in the event handler
                else:
                    data.status = model.MoveRequest.FAILED
                    self.dispatcher(exchange='',
                                    routing_key=props.reply_to,
                                    body=json_encode(data))
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.JoinRequest):
            freecell = [i for i in range(0, self.gameinfo.cellsbyarea()) if i not in self.players.keys()]
            if len(freecell) == 0:
                print("Error: the area is full")
                ch.basic_reject(delivery_tag = method.delivery_tag)
                return
            elif len(freecell) == 1:
                c = freecell[0]
            else:
                c = choice(freecell)
            
            data.player.area = self.id
            data.player.position = c
            data.player.uuid = str(uuid.uuid4())
            self.players[c] = data.player
            self.players[c].last_activity = time()

            print("Accepting new player '%s' at pos %s" % (data.player, c))
            
            # reply to prodedure call
            self.dispatcher(exchange='',
                            routing_key=props.reply_to,
                            body=json_encode(self.gameinfo.playercopy(data.player)))

            # inform other areas and players that a new player joined
            self.dispatcher(exchange='broadcast',
                            routing_key='',
                            body=json_encode(
                            model.Event(model.Event.PLAYER_JOIN, 
                                        player=data.player)))
            
            ch.basic_ack(delivery_tag = method.delivery_tag)
        elif isinstance(data, model.Event):
            # Events are instantly acked
            ch.basic_ack(delivery_tag = method.delivery_tag)
            
            # ~ print("Area %d: %s" % (self.id, data))
            
            if data.type == model.Event.QUIT and data.player in self.players.values():
                self.player_disconnect(data.player, model.Player.DISCONNECT_QUIT)
            elif data.type == model.Event.KEEP_ALIVE and data.player.area == self.id \
                and data.player.position in self.players.keys() \
                and self.players[data.player.position] == data.player:
                self.players[data.player.position].last_activity = time()    
            elif data.type == model.Event.PLAYER_MOVE:
                if data.player in self.players.values() and data.area != self.id:
                    del self.players[list(self.players.keys())[list(self.players.values()).index(data.player)]]      
                    
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
                    
                elif data.player.area + self.gameinfo.nyarea == self.id:
                    if self.id == 0:
                        print ("upper")
                    position_x = data.player.position % self.gameinfo.sxarea
                    position_y = data.player.position // self.gameinfo.sxarea
                    if position_y ==  self.gameinfo.syarea -1 and  position_x in self.players.keys():
                        print ("Me sent "+ str(self.id))
                        self.dispatcher(exchange='broadcast',
                                    routing_key='',
                                    body=json_encode(
                                    model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[position_x], msg=model.Hello.generate(data.player.nickname))))
                elif data.player.area - self.gameinfo.nyarea == self.id:
                    if self.id == 0:
                        print ("lower")
                    position_x = data.player.position % self.gameinfo.sxarea
                    position_y = data.player.position // self.gameinfo.sxarea
                    if position_y == 0 and ((self.gameinfo.syarea - 1) * self.gameinfo.syarea) + position_x in self.players.keys():
                            print ("Me sent "+ str(self.id))
                            self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[((self.gameinfo.syarea - 1) * self.gameinfo.syarea) + position_x], msg=model.Hello.generate(data.player.nickname))))
                elif data.player.area + 1 == self.id and (self.id) % self.gameinfo.nyarea != 0:
                    if self.id == 0:
                        print ("left")
                    position_x = data.player.position % self.gameinfo.sxarea
                    position_y = data.player.position // self.gameinfo.sxarea
                    if position_x == self.gameinfo.syarea-1 and position_y* self.gameinfo.syarea in self.players.keys():
                        print ("Me sent "+ str(self.id))
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[position_y* self.gameinfo.syarea], msg=model.Hello.generate(data.player.nickname))))
                elif data.player.area - 1 == self.id and (self.id + 1) % self.gameinfo.nyarea != 0:
                    if self.id == 0:
                        print ("right")
                    position_x = data.player.position % self.gameinfo.sxarea
                    position_y = data.player.position // self.gameinfo.sxarea
                    if position_x == 0 and position_y*self.gameinfo.syarea + self.gameinfo.sxarea-1  in self.players.keys():
                        print ("Me sent "+ str(self.id))
                        self.dispatcher(exchange='broadcast',
                                        routing_key='',
                                        body=json_encode(
                                        model.Event(model.Event.PLAYER_SAYS, 
                                                    player=self.players[position_y*self.gameinfo.syarea + self.gameinfo.sxarea-1], msg=model.Hello.generate(data.player.nickname))))

                    # for x in range(self.gameinfo.sxarea):
                    #     if (y*self.gameinfo.sxarea + x) in self.players.keys():
                    #         print ("XXXXXXX")
                    #         self.dispatcher(exchange='broadcast',
                    #                     routing_key='',
                    #                     body=json_encode(
                    #                     model.Event(model.Event.PLAYER_SAYS, 
                                                    # player=self.players[y*self.gameinfo.sxarea + x], msg=model.Hello.generate(data.player.nickname))))
                    # ~ print("%d ?%d: x neightboor " % (self.id, data.player.area), abs(data.player.area - self.id) == 1 and int(data.player.area / self.gameinfo.nxarea) == int(self.id / self.gameinfo.nxarea))
                    # ~ print("%d ?%d: y neightboor " % (self.id, data.player.area), abs(data.player.area - self.id) == self.gameinfo.nxarea and data.player.area % self.gameinfo.nxarea == self.id % self.gameinfo.nxarea)                 
                
            elif data.type == model.Event.PLAYER_JOIN:
                self.dispatcher(exchange='broadcast',
                                routing_key='',
                                body=json_encode(
                                model.Event(model.Event.GAME_INFO, players=list(self.players.values()))))
        else:     
            print("Unknown packet: %s" % body)  
            ch.basic_ack(delivery_tag = method.delivery_tag)

    def stop(self):
        self.player_ka_timer.cancel()
