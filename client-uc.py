import socket
import select
import threading
import time
import sys
from PyQt4.QtGui import *


class Client(QWidget):
    def __init__(self, parent=None):
        super(Client, self).__init__(parent)
        self.setWindowTitle('CLient')
        self.layout = QGridLayout(self)
        self.chat = QTextEdit()
        self.input = QLineEdit()
        self.btnUnicast = QPushButton('unicast')
        self.flag = 'unicast'
        self.build()
        self.action()
        self.s1 = self.initUnicast()
        self.name = "anonymous"
        thread_listen = threading.Thread(target=self.listen)
        thread_listen.setDaemon(True)
        thread_listen.start()

    def initUnicast(self):
        s1 = socket.socket()
        s1.connect(('10.42.0.1', 23333))
        return s1

    def sendUnicast(self):
        text = self.input.text()
        text = unicode(text.toUtf8(), 'utf-8', 'ignore')
        text = text.encode("utf-8")
        if self.name == "anonymous":
            self.name = text
        try:
            self.s1.send(text)
        except Exception, e:
            print Exception, ":", e
            self.s1.close()
        self.chat.append(self.name + ': ' + text)
        self.input.clear()
        self.flag = 'unicast'


    def listen(self):
        while True:
            try:
                r, w, e = select.select([self.s1], [], [])
                self.listenUnicast(r)
            except Exception, e:
                print Exception, ":", e
                self.s1.close()
                

    def listenUnicast(self, r):
        if self.s1 in r:
            data = self.s1.recv(1024)
            print 'uni:' + data
            self.chat.append(data)


    def build(self):
        self.layout.addWidget(self.chat, 0, 0, 8, 8)
        self.layout.addWidget(self.input, 8, 0, 1, 6)
        self.layout.addWidget(self.btnUnicast, 8, 6)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)

    def action(self):
        self.btnUnicast.clicked.connect(self.sendUnicast)


app = QApplication(sys.argv)
c = Client()
c.show()
app.exec_()
