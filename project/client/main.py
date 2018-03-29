from package import ui
from package.core import *
from PyQt5.QtWidgets import QApplication
import sys

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
            self.core = GameCore(server, nickname)
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
            
    def onEvent(self, event):
        if event._type == Event.GAME_READY:                        
            self.startdialog.hide()
            
            self.gm.show()
                    
        
c = Controller(sys.argv)
c.run()



