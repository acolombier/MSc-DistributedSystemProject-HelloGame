from copy import copy
from random import choice

class Main:
    @classmethod
    def fromDict(cls, d):
        o = cls()
        o.__dict__.update(d)
        return o

    def serialize(self):
        save_dict = self.__dict__
        save_dict.update({'__type__': self.__class__.__name__})
        return save_dict

    def clean(self):
        return self
        

class Game(Main):
    KEEP_ALIVE_TIMEOUT = 4
    GRACE_TIME = 2
    
    def __init__(self, nxarea=0, nyarea=0, sxarea=0, syarea=0, player=None):
        self.nxarea = nxarea
        self.nyarea = nyarea
        self.sxarea = sxarea
        self.syarea = syarea
        self.player = player
        self.area_color = [13 for i in range(0, nxarea * nyarea)]
        
    def playercopy(self, player):
        ret = copy(self)
        ret.player = player
        return ret


class Player(Main):
    
    DISCONNECT_QUIT = 0x0
    DISCONNECT_TIMEOUT = 0x1
    DISCONNECT_KICK = 0x2
    
    AVAILABLE_COLOR = [3,  #	White (#ffffff)
                       7,  #	Red (#ff0000)
                       8,  #	Green (#00ff00)
                       9]  #	Blue (#0000ff)
    
    def __init__(self, nickname=None):
        self.nickname = nickname
        self.area = None
        self.position = None
        self.uuid = None
        self.color = choice(Player.AVAILABLE_COLOR)
        
    def is_on_board(self):
        return self.area is not None and self.position is not None
        
    def __eq__(self, other):
        return isinstance(other, Player) and self.uuid == other.uuid
        
    def __repr__(self):
        return "<Player %s>" % (self)
        
    def __repr__(self):
        return "%s [%s]" % (self.nickname, self.uuid)
        
    def clean(self):
        _self = copy(self)
        if hasattr(self, "last_activity"):
            del _self.last_activity
        return _self
 
        
class Request(Main):
    
    SUCCESS = 0x0
    PENDING = 0x1     
    FAILED = 0x2    
       
class MoveRequest(Request):
    
    def __init__(self, player=None, area=None, pos=None):
        super().__init__()
        self.player = player
        self.destination = (area, pos)  
        self.status = MoveRequest.PENDING
        
    def area(self):
        return self.destination[0]
        
    def cellid(self):
        return self.destination[1]
            
class JoinRequest(Request):
    
    def __init__(self, player=None):
        super().__init__()
        self.player = player

             
class Event(Main):
    
    UNKNOWN = 0xFFFF
    
    PLAYER_MOVE = 0x0
    PLAYER_SAYS = 0x1
    PLAYER_JOIN = 0x2
    
    GAME_READY = 0x10
    GAME_INFO = 0x11
    
    KEEP_ALIVE = 0x20
    
    QUIT = 0xF0
    
    ERROR = 0xFF
    
    
    def __init__(self, _type=UNKNOWN, **args):
        self.type = _type
        self.__dict__.update(args)
        
    def typename(self):
        return list(Event.__dict__.keys())[list(Event.__dict__.values()).index(self.type)]
        
    def __repr__(self):
        return "<Event:%s %s>" % (self.typename(), [i for k, i in self.__dict__.items() if k != "type"])
        
    def __iter__(self):
        print(self.__dict__.keys())
        return (getattr(self, x) for x in self.__dict__.keys() if x != "type")
 
        
class Hello:
    AVAILABLE_MSG = ["Bonjour %s!", 
                     "Hello %s!", 
                     "你好 %s!", 
                     "%s مرحبا!", 
                     "Guten tage %s!"]
    
    @classmethod
    def generate(cls, nickname):
        return choice(Hello.AVAILABLE_MSG) % nickname
 
        
class Letsgo:
    AVAILABLE_MSG = ["C'est parti!", "Let's go!", "Los geht's!"]
    
    @classmethod
    def generate(cls):
        return choice(Letsgo.AVAILABLE_MSG)
