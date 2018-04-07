from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QPropertyAnimation
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from random import choice

from threading import Event

from .template.startdialog import Ui_StartDialog

class Area(QWidget):
    requestedPosition = pyqtSignal(int)
    
    COLOR = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.cyan, Qt.magenta]
    
    def __init__(self, width=4, height=4, *args):
        super().__init__(*args)
        self.nrow = width
        self.ncol = height
        
        self.color = choice(Area.COLOR)
    
        self.setMinimumSize(40 * self.nrow, 40 * self.ncol)
        
    def cellsize(self):
        return QSize(self.width() / self.ncol, self.height() / self.nrow)
        
    def cellpos(self, cellid):
        x_size, y_size = self.width() / self.ncol, self.height() / self.nrow
        
        print(cellid, x_size, y_size, (cellid % self.ncol) * x_size, int(cellid / self.nrow) * y_size)
        
        return self.pos() + QPoint((cellid % self.ncol) * x_size, int(cellid / self.nrow) * y_size)
        
    def mousePressEvent(self, event):
        x_size, y_size = self.width() / self.ncol, self.height() / self.nrow
        
        if event.button() == Qt.LeftButton:
            cell_clicked = int(event.y() / y_size) * self.ncol + int(event.x() / x_size)
            self.requestedPosition.emit(cell_clicked)
            
        
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(self.color)
        for i in range(0, self.nrow+1):
            p.drawLine((self.width() / self.nrow) * i, 0, (self.width() / self.nrow) * i, self.height())   
        for i in range(0, self.ncol+1):
            p.drawLine(0, (self.height() / self.ncol) * i, self.width(), (self.height() / self.ncol) * i)      
        p.end()
        
        
class Board(QWidget):
    
    requestedPosition = pyqtSignal(int, int)
    def __init__(self, width=2, height=2, **kwargs):
        super().__init__(**kwargs)
        self.w = width
        self.h = height
        
        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        self.players = {}
        self.area = []
        
        for w in range(0, width):
            for h  in range(0, height):
                self.area.append(Area(**kwargs))
                self.layout().addWidget(self.area[-1], w, h)
                self.area[-1].requestedPosition.connect((lambda a: (lambda p: self.moveTo(a, p)))(self.area[-1]))
                
    def moveTo(self, area, pos):
        self.requestedPosition.emit(self.area.index(area), pos)
                
    def addplayer(self, player):
        if player.uuid not in self.players.keys():
            self.players[player.uuid] = Player(player.area, player.position)
            self.players[player.uuid].setParent(self)
            self.players[player.uuid].moveTo(player.area, player.position)
            # ~ print(self.area[player.area].cellpos(player.position))
            # ~ self.players[player.uuid].move(self.area[player.area].cellpos(player.position))
            
    def moveplayer(self, player):
        if player.uuid not in self.players.keys():
            sefl.addplayer(player)
        else:
            self.players[player.uuid].animateTo(player.area, player.position)
        
    
    def saysplayer(self, player, msg):
        if player.uuid not in self.players.keys():
            sefl.addplayer(player)
        self.players[player.uuid].animateSays(msg)
        
            
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(Qt.gray)
        
        p.drawLine(0, 0, 0, self.height())   
        p.drawLine(self.width(), 0, self.width(), self.height())   
        p.drawLine(0, 0, self.width(), 0)   
        p.drawLine(0, self.height(), self.width(), self.height())   
        
        p.end()
        
        
        
class Player(QWidget):
    def __init__(self, area, position, **kwargs):
        super().__init__()
        
        self.setMinimumSize(40, 40)
        
        self.posAnimation = None
        
    def moveTo(self, area, position):
        self.area = area
        self.position = position
        
        self.move(self.parent().area[self.area].cellpos(self.position))
        self.show()
        self.raise_()
        
    def resizeEvent(self, e):
        self.move(self.parent().area[self.area].cellpos(self.position))        
        self.resize(self.parent().area[self.area].cellsize())
                
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.white)
        p.drawEllipse(0, 0, self.width(), self.height()) 
        p.setBrush(Qt.black)
        
        p.drawEllipse(self.width() / 4 - 5, self.width() / 4 - 5, 10, 10)      
        p.drawEllipse(3 * (self.width() / 4) - 5, self.width() / 4 - 5, 10, 10)
              
        p.end()
        
    def animateTo(self, area, position):
        if isinstance(QPropertyAnimation, self.posAnimation):
            self.posAnimation.stop()
        
        self.posAnimation = QPropertyAnimation(myWidget, "pos")
        self.posAnimation.setDuration(3000)
        self.posAnimationsetStartValue(self.pos())
        self.posAnimationsetEndValue(self.parent().area[area].cellpos(position))

        self.posAnimationstart()            
        
    
    def animateSays(self, msg):
        QTimer.singleShot(3000, self.messageoff)
        
    def animateSays(self, msg):
        self.messageoff = False
        self.update()
        

class GameWindow(QMainWindow):
    requestedPosition = pyqtSignal(int, int)
    closed = pyqtSignal()
    
    def __init__(self, *args):
        super().__init__(*args)
        
        icon = QIcon()
        icon.addPixmap(QPixmap("res/favicon.jpg"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("Hello Game - Game running")
        
        self.board = Board()
        self.setCentralWidget(self.board)
        
        self.board.requestedPosition.connect(lambda a, p: self.requestedPosition.emit(a, p))
        
    def closeEvent(self, event):
        self.closed.emit()
        
        QMainWindow.closeEvent(self, event)

        
        
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
        self.ui.nicknameValue.setEnabled(False)
        self.ui.serverValue.setEnabled(False)
        self.ui.ConnectButton.setEnabled(False)
        self.ui.errorMsgText.setText("Connecting...")
        self.submited.emit(self.ui.nicknameValue.text(), self.ui.serverValue.text())
        
    def error(self, msg):
        self.sent.clear()
        self.ui.nicknameValue.setEnabled(True)
        self.ui.serverValue.setEnabled(True)
        self.ui.ConnectButton.setEnabled(True)
        self.ui.errorMsgText.setText("<b style='color: red;'>%s</b>" % msg)
        
    def status(self, msg):
        self.ui.errorMsgText.setText("<i style='color: grey;'>%s</i>" % msg)
    
