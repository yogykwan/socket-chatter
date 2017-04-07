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
        self.btnMulticast = QPushButton('multicast')
        self.flag = 'unicast'
        self.build()
        self.action()
        self.s1 = self.initUnicast()
        self.s2 = self.initMulticast()
        self.name = "anonymous"
        thread_listen = threading.Thread(target=self.listen)
        thread_listen.setDaemon(True)
        thread_listen.start()

    def initUnicast(self):
        s1 = socket.socket()
        s1.connect(('localhost', 2333))
        return s1

    def initMulticast(self):
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        s2.bind(('', 23333))
        intf = socket.gethostbyname(socket.gethostname())
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                      socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
        s2.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                      socket.inet_aton('239.0.0.222') + socket.inet_aton('0.0.0.0'))
        return s2

    def sendUnicast(self):
        text = self.input.text()
        text = unicode(text.toUtf8(), 'utf-8', 'ignore')
        data = text.encode("utf-8")
        if self.name == "anonymous":
            self.name = text
        try:
            self.s1.send(data)
        except Exception, e:
            print Exception, ":", e
            self.s1.close()
            self.s2.close()
        self.chat.append(self.name + ': ' + data)
        self.input.clear()
        self.flag = 'unicast'

    def sendMulticast(self):
        text = self.input.text()
        text = unicode(text.toUtf8(), 'utf-8', 'ignore')
        data = self.name + ': ' + text.encode("utf-8")
        try:
            self.s2.sendto(data, ('239.0.0.222', 23333))
        except Exception, e:
            print Exception, ":", e
            self.s1.close()
            self.s2.close()
        self.chat.append(data)
        self.input.clear()
        self.flag = 'multicast'

    def listen(self):
        while True:
            # if self.flag == 'unicast':
            #     self.listenUnicast()
            # else:
            #     self.listenMulticast()
            # time.sleep(3)
            try:
                r, w, e = select.select([self.s1, self.s2], [], [])
                self.listenUnicast(r)
                self.listenMulticast(r)
                print 'listen'
            except Exception, e:
                print Exception, ":", e
                self.s1.close()
                self.s2.close()

    def listenUnicast(self, r):
        # r, w, e = select.select([self.s1], [], [])
        if self.s1 in r:
            data = self.s1.recv(1024)
            print 'uni:' + data
            self.chat.append(data)

    def listenMulticast(self, r):
        # r, w, e = select.select([self.s2], [], [])
        if self.s2 in r:
            data, sender_addr = self.s2.recvfrom(1024)
            print 'multi:' + data
            self.chat.append(data)

    def build(self):
        self.layout.addWidget(self.chat, 0, 0, 8, 8)
        self.layout.addWidget(self.input, 8, 0, 1, 6)
        self.layout.addWidget(self.btnUnicast, 8, 6)
        self.layout.addWidget(self.btnMulticast, 8, 7)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)

    def action(self):
        self.btnUnicast.clicked.connect(self.sendUnicast)
        self.btnMulticast.clicked.connect(self.sendMulticast)


app = QApplication(sys.argv)
c = Client()
c.show()
app.exec_()
