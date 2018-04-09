from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QPropertyAnimation, QTimer
from PyQt5.QtGui import QPainter, QIcon, QPixmap, QFont
from random import choice
from math import sqrt

from threading import Event

from .template.startdialog import Ui_StartDialog

class Area(QWidget):
    requestedPosition = pyqtSignal(int)
    
    def __init__(self, width=4, height=4, color=13, *args):
        super().__init__(*args)
        self.nrow = height
        self.ncol = width
        
        self.color = Qt.GlobalColor(color)
    
        self.setMinimumSize(40 * self.ncol, 40 * self.nrow)
        
    def cellsize(self):
        return QSize(self.width() / self.ncol, self.height() / self.nrow)
        
    def cellpos(self, cellid):
        x_size, y_size = self.width() / self.ncol, self.height() / self.nrow
        
        return self.pos() + QPoint((cellid % self.ncol) * x_size, int(cellid / self.ncol) * y_size)
        
    def mousePressEvent(self, event):
        x_size, y_size = self.width() / self.ncol, self.height() / self.nrow
        
        if event.button() == Qt.LeftButton:
            cell_clicked = int(event.y() / y_size) * self.ncol + int(event.x() / x_size)
            self.requestedPosition.emit(cell_clicked)
            
        
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(self.color)
        for i in range(0, self.ncol+1):
            p.drawLine((self.width() / self.ncol) * i, 0, (self.width() / self.ncol) * i, self.height())   
        for i in range(0, self.nrow+1):
            p.drawLine(0, (self.height() / self.nrow) * i, self.width(), (self.height() / self.nrow) * i)      
        p.end()
        
        
class Board(QWidget):
    
    requestedPosition = pyqtSignal(int, int)
    
    def __init__(self, row=2, col=2, area_width=4, area_height=4, area_color=[], **kwargs):
        super().__init__(**kwargs)
        self.w = row
        self.h = col
        
        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        self.players = {}
        self.area = []
        
        for w in range(0, col):
            for h  in range(0, row):
                self.area.append(Area(area_width, area_height, area_color[h * col + w], **kwargs))
                self.layout().addWidget(self.area[-1], w, h)
                self.area[-1].requestedPosition.connect((lambda a: (lambda p: self.moveTo(a, p)))(self.area[-1]))
                
    def moveTo(self, area, pos):
        self.requestedPosition.emit(self.area.index(area), pos)
                
    def addplayer(self, player):
        if player.uuid not in self.players.keys():
            self.players[player.uuid] = Player(player.area, player.position, player.nickname, player.color)
            self.players[player.uuid].setParent(self)
            self.players[player.uuid].moveTo(player.area, player.position)
            
    def delplayer(self, player):
        if player.uuid in self.players.keys():
            self.players[player.uuid].hide()
            del self.players[player.uuid]
            self.update()
            
    def moveplayer(self, player):
        if player.uuid not in self.players.keys():
            self.addplayer(player)
        else:
            self.players[player.uuid].animateTo(player.area, player.position)
        
    
    def saysplayer(self, player, msg):
        if player.uuid not in self.players.keys():
            self.addplayer(player)
        self.players[player.uuid].animateSays(msg)
     
    
    def resizeEvent(self, e):
        for p in self.players.values():
            p.resizeEvent(e)
            
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(Qt.gray)
        
        p.drawLine(0, 0, 0, self.height())   
        p.drawLine(self.width(), 0, self.width(), self.height())   
        p.drawLine(0, 0, self.width(), 0)   
        p.drawLine(0, self.height(), self.width(), self.height())   
        
        p.end()
        
        
        
class Player(QWidget):
    def __init__(self, area, position, nickname, color, **kwargs):
        super().__init__()
        
        self.setMinimumSize(40, 40)
        
        self.setToolTip(nickname)
        
        self.color = Qt.GlobalColor(color)
        
        self.message = None
        self.textbubble = None
        self.posAnimation = None
        self.says_timer = None
        
    def moveTo(self, area, position):
        self.area = area
        self.position = position
        
        self.move(self.parent().area[self.area].cellpos(self.position))    
        self.resize(self.parent().area[self.area].cellsize())
        self.show()
        self.raise_()
        
    def resizeEvent(self, e):
        self.move(self.parent().area[self.area].cellpos(self.position))        
        self.resize(self.parent().area[self.area].cellsize())
                
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        p.drawEllipse(0, 0, self.width(), self.height()) 
        p.setBrush(Qt.black)
        
        
        p.drawEllipse(self.width() / 4 - 5, self.width() / 4 - 5, 10, 10)      
        p.drawEllipse(3 * (self.width() / 4) - 5, self.width() / 4 - 5, 10, 10)
        
        if self.textbubble:
            self.textbubble.update()
              
        p.end()
        
    def animateTo(self, area, position):
        if isinstance(self.posAnimation, QPropertyAnimation):
            self.posAnimation.stop()
        
        distance = sqrt((self.pos().x() - self.parent().area[area].cellpos(position).x()) ** 2 + (self.pos().y() - self.parent().area[area].cellpos(position).y()) ** 2)
        
        self.area = area
        self.position = position
        
        self.posAnimation = QPropertyAnimation(self, b"pos")
        self.posAnimation.setDuration(distance * 8)
        self.posAnimation.setStartValue(self.pos())
        self.posAnimation.setEndValue(self.parent().area[area].cellpos(position))

        self.posAnimation.start()      
        
    def animateSays(self, msg):
        if msg == self.message:
            return
        self.message = msg
        
        if self.textbubble:
            self.textbubble.hide()
            del self.textbubble
            self.textbubble = None
            if self.says_timer is not None:
                self.says_timer.cancel()
            
        if self.message:
            self.textbubble = TextBubble(self, self.message)
            
        self.update()
        self.says_timer = QTimer.singleShot(3000, lambda: self.animateSays(None))
        
class TextBubble(QWidget):
    def __init__(self, player, text):
        super().__init__()
        self.player = player
        self.text = text
        
        self.setParent(player.parent())
        self.show()
        self.raise_()
        self.resize(10, 10)
        
    def paintEvent(self, event):
        p = QPainter(self)
        
        font = QFont()        
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        p.setFont(font)
        
        p.setPen(Qt.black)
        p.setBrush(self.player.color)
        txt_s = p.fontMetrics().width(self.text) + 4, p.fontMetrics().height() + 4
        
        (self.x() + self.width() / 4 - 5, self.y() + self.width() / 4 - 5)
        
        xpos = (self.player.x() + self.player.width() / 4 - 5) - txt_s[0]
        if xpos < 0: xpos = (self.player.x() + 3 * (self.player.width() / 4) + 5)
        
        ypos = (self.player.y() + self.height() / 4 - 5) - txt_s[1] + 4
        if ypos < 0: ypos = (self.player.y() + self.height() / 4 - 5) + txt_s[1] + 4
        
        if self.pos() != QPoint(xpos, ypos) or self.size() != QSize(txt_s[0] + 4, txt_s[1] + 4):
            self.move(xpos, ypos)
            self.resize(txt_s[0] + 4, txt_s[1] + 4)
            p.end()
            self.update()
            return      
        
        p.drawRoundedRect(0, 0, *txt_s, 4, 4)
        p.drawText(2, txt_s[1] - 4, self.text)
              
        p.end()    

class GameWindow(QMainWindow):
    requestedPosition = pyqtSignal(int, int)
    closed = pyqtSignal()
    
    def __init__(self, *args):
        super().__init__()
        
        icon = QIcon()
        icon.addPixmap(QPixmap("res/favicon.jpg"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("Hello Game - Game running")
        
        self.board = Board(*args)
        self.setCentralWidget(self.board)
        
        self.board.requestedPosition.connect(lambda a, p: self.requestedPosition.emit(a, p))
        
    def closeEvent(self, event):
        self.closed.emit()
        
        QMainWindow.closeEvent(self, event)

        
        
class GameStartDialog(QDialog):
    submited = pyqtSignal(str, str)
    closed = pyqtSignal()
    
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
        
    def closeEvent(self, event):
        self.closed.emit()
    
