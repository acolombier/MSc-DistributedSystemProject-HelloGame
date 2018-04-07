from copy import copy

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
    
    def __init__(self, nxarea=None, nyarea=None, sxarea=None, syarea=None, player=None):
        self.nxarea = nxarea
        self.nyarea = nyarea
        self.sxarea = sxarea
        self.syarea = syarea
        self.player = player
        
    def playercopy(self, player):
        ret = copy(self)
        ret.player = player
        return ret


class Player(Main):
    
    DISCONNECT_QUIT = 0x0
    DISCONNECT_TIMEOUT = 0x1
    DISCONNECT_KICK = 0x2
    
    def __init__(self, nickname=None):
        self.nickname = nickname
        self.area = None
        self.position = None
        self.uuid = None
        
    def is_on_board(self):
        return self.area is not None and self.position is not None
        
    def __eq__(self, other):
        return isinstance(other, Player) and self.uuid == other.uuid
        
    def clean(self):
        _self = copy(self)
        if hasattr(self, "last_activity"):
            del _self.last_activity
        return _self
 
        
class Request(Main):
    
    PENDING = 0x0
    FAILED = 0x1     
       
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
        
    def __iter__(self):
        print(self.__dict__.keys())
        return (getattr(self, x) for x in self.__dict__.keys() if x != "type")