from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QIcon, QPixmap

from threading import Event

from .template.startdialog import Ui_StartDialog

class Area(QWidget):
    requestedPosition = pyqtSignal(int)
    def __init__(self, width=4, height=4, *args):
        super().__init__(*args)
        self.nrow = width
        self.ncol = height
        
    
        self.setMinimumSize(40 * self.nrow, 40 * self.ncol)
        
    def cellpos(self, cellid):
        x_size, y_size = self.width(), self.height()
        x_size /= self.nrow
        y_size /= self.ncol
        
        return QSize((cellid % self.nrow) * x_size, (cellid / self.nrow) * y_size)
        
    def mousePressEvent(self, event):
        x_size, y_size = self.event.x(), self.event.y()
        x_size /= self.nrow
        y_size /= self.ncol
        
        if event.button() == Qt.LeftButton:
            cell_clicked = (event.y() / y_size) + (event.x() / x_size)
            
            print("clicking cell %d" % cell_clicked)
            
        
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
        self.area = []
        
        for w in range(0, width):
            for h  in range(0, height):
                self.area.append(Area(**kwargs))
                self.layout().addWidget(self.area[-1], w, h)
                
    def addplayer(self, player):
        self.players[hash(player)] = Player(self)
        self.players[hash(player)].move(self.area[player.area].pos() + self.area[player.area].cellpos(player.position))
        
        
class Player(QWidget):
    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        
        self.setFixedSize(40, 40)
                
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
        
        self.sent = Event()
        self.sent.clear()
        
        self.ui.nicknameValue.returnPressed.connect(self.submit)
        self.ui.serverValue.returnPressed.connect(self.submit)
        self.ui.ConnectButton.clicked.connect(self.submit)
        
    def submit(self):
        if self.sent.is_set():
            return
        self.sent.set()
        self.ui.errorMsgText.setText("Connecting...")
        self.submited.emit(self.ui.nicknameValue.text(), self.ui.serverValue.text())
        
    def error(self, msg):
        self.sent.clear()
        self.ui.errorMsgText.setText("<b style='color: red;'>%s</b>" % msg)
        
    def status(self, msg):
        self.ui.errorMsgText.setText("<i style='color: grey;'>%s</i>" % msg)
    
