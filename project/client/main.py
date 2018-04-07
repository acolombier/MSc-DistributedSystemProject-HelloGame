#!/usr/bin/env python3
from package import ui
from package.core import *
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys
from threading import Thread

class Controller(QApplication):

    def __init__(self, *args):
        super().__init__(*args)
        
        self.startdialog = ui.GameStartDialog()
        self.gm = ui.GameWindow()
        
        self.startdialog.submited.connect(self.launchGame)
        if len(args) == 3:
            self.startdialog.ui.nicknameValue.text(args[2])
            self.startdialog.ui.serverValue.text(args[1])
        
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
            
            self.core.register()
            
        except GameStartException as e:
            self.startdialog.error(str(e))
            
    def onEvent(self, event):
        if event.type == model.Event.GAME_READY:                        
            self.startdialog.hide()
            
            self.gm.requestedPosition.connect(self.core.movePlayer)
            self.gm.closed.connect(self.core.stop)
            
            ## Build the board out of the sent data (nb areas, area size, players)
            
            self.gm.show()
        elif event.type == model.Event.PLAYER_JOIN:  
            self.gm.board.addplayer(event.player)
        elif event.type == model.Event.PLAYER_MOVE:  
            self.gm.board.moveplayer(event.player)
        elif event.type == model.Event.PLAYER_SAYS:  
            self.gm.board.saysplayer(event.player, event.msg)
        elif event.type == model.Event.ERROR:  
            if self.gm.isVisible():
                QMessageBox.critical(self.gm, "Error", event.msg)
            else:
                self.startdialog.error(event.msg)
        elif event.type != model.Event.KEEP_ALIVE:
            print("Unknown event:", event.__dict__)
                    
        
c = Controller(sys.argv)
c.run()



