from package import ui
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
            self.core = GameCore(server, nickname, listener=self.gm)
            
            self.startdialog.hide()
            
            self.gm.show()
        except GameStartException as e:
            self.startdialog.error(str(e))
        
        
c = Controller(sys.argv)
c.run()



