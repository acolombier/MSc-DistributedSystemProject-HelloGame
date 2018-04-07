import pika
from .model import *
from .serializer import *
from multiprocessing import Queue
from threading import Event, Thread, Lock

from socket import gaierror
import pickle

from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication, QTimer


class GameStartException(Exception):
    def __init__(self, *args):
        super().__init__(*args)   

class TiemoutException(Exception):
    def __init__(self, *args):
        super().__init__(*args)    

    
class DispatchTask:
    def __init__(self, callback, *args):
        self.args = args
        self.callback = callback
        self.ready = None
        self.result = None
        
    def __call__(self, ctx):
        self.result = self.callback(ctx, *self.args)
        if self.ready is None:
            self.ready = Event()
        self.ready.set()
        
    def get(self):
        if self.ready is None:
            self.ready = Event()
        self.ready.wait()
        return self.results
    
class GameCore(QThread):
    eventReceived = pyqtSignal(object)
    statusChanged = pyqtSignal(str)
    errorEncounted = pyqtSignal(str)
    finished = pyqtSignal()
    
    BROADCAST = 0x0
    DIRECT = 0x1
    
    def __init__(self, nickname, server):
        super().__init__()
        
        self.server, self.player = server, Player(nickname)
        self.isrunning = True
        
        self._pending_requests = Queue()
        
        self.isready = Event()
        self.isregistered = Event()
        
        self.rmq = Lock()
        
        self.keep_alive_timer = QTimer(self)
        self.keep_alive_timer.timeout.connect(self.keep_alive)
        self.keep_alive_timer.start(2000)
        
        self.dispatcher_thread = Thread(target=self.dispatcher)
        self.dispatcher_thread.start()
        
        print ("Initialising a game on %s with the nickname '%s'" % (server, nickname))
        
    """
    The dispatch return the pending task (usefull ta asynchronously get the result for RPC call). use the method get from the DispatcherTask to do so
    
    You can pass it even straight away, and the method will build up the correct DispatcherTask
    I.e: core.dispatch(model.Event(model.Event.QUIT)) or core.dispatch(model.Event(<EVENT>), GameCore.BROADCAST)
    """
    def dispatch(self, callhandler, *args):
        if isinstance(callhandler, model.Event):
            task = DispatchTask(GameCore._send, callhandler, *args)
        else:
            task = DispatchTask(callhandler, *args)
        self._pending_requests.put(task)
        return task
        
    def dispatcher(self):
        while self.isrunning:
            task = self._pending_requests.get()
            if task is not None:
                task(self)
      
    def init(self):
        
        self.statusChanged.emit("Connection to server...")
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server))
            
        except gaierror as e:
            self.errorEncounted.emit(str(e))
            self.stop()
            
            return False


        self.channel = self.connection.channel()
        self.replies = Queue()
        
        self.channel.exchange_declare(exchange='broadcast',
                                      exchange_type='fanout')
        bc_queue = self.channel.queue_declare(exclusive=True)
        broadcast_queue_name = bc_queue.method.queue

        self.channel.queue_bind(exchange='broadcast',
                                queue=broadcast_queue_name)

        ### RPC Reply Channel
        reply_to_queue = self.channel.queue_declare(exclusive=True)
        self.callback_queue = reply_to_queue.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
                                   
        ### Main Broadcast Channel
        self.channel.basic_consume(self.on_broadcast,
                                   queue=broadcast_queue_name)
        return True
        
      
    #################################
    #  One way interaction methods  #
    #################################
    
    def keep_alive(self):    
        if self.player.is_on_board():
            self.dispatch(model.Event(model.Event.KEEP_ALIVE, player=self.player))
        
    def stop(self):
        self.keep_alive_timer.stop()
        if self.player.is_on_board():
            self.dispatch(model.Event(model.Event.QUIT, player=self.player))
        self.isrunning = False
        self._pending_requests.put(None)
        self.dispatcher_thread.join()
        
      
    #################################
    #  Two way interaction methods  #
    #################################
    
    def register(self):
        self.dispatch(GameCore._register)
        
    def _register(self):
        try:
            self.statusChanged.emit("Accessing to the game...")
            gameinfo = self._request(JoinRequest(self.player))
            
            assert gameinfo.player.nickname == self.player.nickname
            self.player = gameinfo.player
            
            self.statusChanged.emit("Connected")
            self.eventReceived.emit(model.Event(model.Event.GAME_READY, gameinfo=gameinfo))
            self.isregistered.set()
        except TiemoutException:
            self.eventReceived.emit(model.Event(model.Event.ERROR, msg="Game server couldn't be reached."))
        
    def movePlayer(self, area, pos):
        self.dispatch(GameCore._movePlayer, area, pos)
        
    def _movePlayer(self, area, pos):
        try:
            reply = self._request(MoveRequest(self.player, area, pos))
            if reply.status != model.MoveRequest.SUCCESS:
                self.eventReceived.emit(model.Event(model.Event.ERROR, msg="You cannot move their")) 
            else:
                self.player.area, self.player.position = reply.player.area, reply.player.position
        except TiemoutException:
            self.eventReceived.emit(model.Event(model.Event.ERROR, msg="Game server connexion is lost."))
        
     
    #####################
    #  Handler methods  #
    #####################
       
    def on_response(self, ch, method, props, body):
        data = json_decode(body)
        self.replies.put(data)
        
    def on_broadcast(self, ch, method, props, body):
        data = json_decode(body)
        
        if isinstance(data, model.Event):
            self.isregistered.wait()
            self.eventReceived.emit(data)  
            # TODO : We should handel the receiption of SAY_HELLO_EVENT          
            # It is done in the event receiver handler (see Controller::onEvent, main.py:68)
            
        ch.basic_ack(delivery_tag = method.delivery_tag)
        
    # Must not be called directly! Only with the dispatcher to ensure the thread safety
    def _send(self, data, _type=0x1):
        try:
            self.rmq.acquire()
            self.channel.basic_publish(exchange='',
                                       routing_key='main_queue' if not self.player.is_on_board() or _type == GameCore.BROADCAST 
                                            else "node_area_%d" % self.player.area,
                                       body=json_encode(model.Event(model.Event.KEEP_ALIVE, player=self.player)))
        finally:
            self.rmq.release()
            

    def _request(self, payload):
        self.isready.wait()
        assert self.replies.empty()
        
        try:
            self.rmq.acquire()
            self.channel.basic_publish(exchange='',
                                       routing_key='main_queue' if not self.player.is_on_board() else "node_area_%d" % self.player.area,
                                       properties=pika.BasicProperties(
                                             reply_to = self.callback_queue
                                             ),
                                       body=json_encode(payload))
        finally:
            self.rmq.release()
            
        try:
            return self.replies.get(timeout=5)
        except Exception:
            raise TiemoutException()
        
        
    def run(self):
        if self.init():
            self.isready.set()
            while self.isrunning:
                try:
                    self.rmq.acquire()
                    self.connection.process_data_events()
                finally:
                    self.rmq.release()
                QCoreApplication.instance().processEvents()
        self.finished.emit()

