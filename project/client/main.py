from package import ui
from package.core import *
from PyQt5.QtWidgets import QApplication
import sys
from threading import Thread

class Controller(QApplication):

    def __init__(self, *args):
        super().__init__(*args)
        
        self.startdialog = ui.GameStartDialog()
        
        self.startdialog.submited.connect(self.launchGame)
        
        self.gm = ui.GameWindow()
        
    def run(self):
        self.startdialog.show()
        self.exec()
        
    def launchGame(self, nickname, server):
        try:
            self.core = GameCore(nickname, server)
            self.core.statusChanged.connect(self.startdialog.status)
            self.core.errorEncounted.connect(self.startdialog.error)
            self.core.eventReceived.connect(self.onEvent)
            
            self.corethread = QThread()
            self.core.moveToThread(self.corethread)
            self.corethread.finished.connect(self.core.deleteLater)
            self.corethread.started.connect(self.core.run)
            self.core.finished.connect(self.corethread.quit)
            self.corethread.start()
            
        except GameStartException as e:
            self.startdialog.error(str(e))
            
        Thread(target=self.core.register).start()
            
    def onEvent(self, event):
        if event.type == model.Event.GAME_READY:                        
            self.startdialog.hide()
            
            ## Build the board out of the sent data (nb areas, area size, players)
            
            self.gm.show()
        elif event.type == model.Event.PLAYER_JOIN:  
            self.gm.board.addplayer(event.player)
        else:
            print("Unknown event:", event.__dict__)
                    
        
c = Controller(sys.argv)
c.run()



