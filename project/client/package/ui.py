from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QIcon, QPixmap

from .template.startdialog import Ui_StartDialog

class Area(QWidget):
    def __init__(self, width=4, height=4, *args):
        super().__init__(*args)
        self.nrow = width
        self.ncol = height
        
    def cellpos(self, x, y):
        return x * (self.width() / self.width), y * (self.height() / self.ncol)
        
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(Qt.red)
        for i in range(0, self.nrow+1):
            p.drawLine((self.width() / self.nrow) * i, 0, (self.width() / self.nrow) * i, self.height())   
        for i in range(0, self.ncol+1):
            p.drawLine(0, (self.height() / self.ncol) * i, self.width(), (self.height() / self.ncol) * i)      
        p.end()
        
        
class Board(QWidget):
    def __init__(self, width=2, height=2, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        
        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)
        
        self.players = {}
        
        for w in range(0, width):
            for h  in range(0, height):
                self.layout().addWidget(Area(**kwargs), w, h)
                
    def addplayer(self, player, area, coordinate):
        self.players[hash(player)] = (area, coordinate)
        player.setParent(self)
        player.move(area.pos() + area.cellpos(*coordinate))
        
        
class Player(QWidget):
    def __init__(self, width=2, height=2, **kwargs):
        super().__init__(args)
        self.width = width
        self.height = height
        
        self.setlayout(QGridLayout())
        
        self.players = []
        
        for w in range(0, width):
            for h  in range(0, height):
                self.layout().addWidget(Area(**kwargs))
                
    def paintevent(self, event):
        p = QPainter(self)
        
        p.setpen(Qt.blue)
        p.drawElipse(0, 0, self.width() / 2, self.height() / 2)      
        p.end()
        

class GameWindow(QMainWindow):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        icon = QIcon()
        icon.addPixmap(QPixmap("res/favicon.jpg"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("Hello Game - Game running")
        
        self.board = Board()
        self.setCentralWidget(self.board)
        
        
class GameStartDialog(QDialog):
    submited = pyqtSignal(str, str)
    
    def __init__(self, *args):
        super().__init__(*args)
        self.ui = Ui_StartDialog()
        self.ui.setupUi(self)
        
        self.ui.nicknameValue.returnPressed.connect(self.submit)
        self.ui.serverValue.returnPressed.connect(self.submit)
        self.ui.ConnectButton.clicked.connect(self.submit)
        
    def submit(self):
        self.ui.errorMsgText.setText("Connecting...")
        self.submited.emit(self.ui.nicknameValue.text(), self.ui.serverValue.text())
        
    def error(self, msg):
        self.ui.errorMsgText.setText("<b style='color: red;'>%s</b>" % msg)
        
    def status(self, msg):
        self.ui.errorMsgText.setText("<i style='color: grey;'>%s</i>" % msg)
    
