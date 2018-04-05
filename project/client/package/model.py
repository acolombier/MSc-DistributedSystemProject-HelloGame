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

class Player(Main):
    def __init__(self, nickname=None):
        self.nickname = nickname
        self.area = None
        self.position = None
        
    def is_on_board(self):
        return self.area is not None and self.position is not None
 
        
class Request(Main):
    
    PENDING = 0x0
    FAILED = 0x1     
       
class MoveRequest(Request):
    
    def __init__(self, player, area, x, y):
        super().__init__()
        self.player = player
        self.destination = (area, x, y)  
        self.status = MoveRequest.PENDING
        
    def area(self):
        return self.destination[0]
        
    def x(self):
        return self.destination[1]
        
    def y(self):
        return self.destination[2]
            
class JoinRequest(Request):
    
    def __init__(self, player=None):
        super().__init__()
        self.player = player

             
class Event(Main):
    
    UNKNOWN = 0xFFFF
    
    PLAYER_MOVE = 0x0
    PLAYER_SAYS = 0x1
    PLAYER_JOIN = 0x2
    
    GAME_READY = 0x3
    
    def __init__(self, _type=UNKNOWN, **args):
        self.type = _type
        self.__dict__.update(args)
        self.args = list(args.values())
