import socket
import select
import time


users = []
names = {}


def connect():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('10.42.0.1', 23333))
    s.listen(10)
    return s


def newer(s):
    client, add = s.accept()
    client.send('Enter your name:')
    name = client.recv(1024)
    users.append(client)
    names[client] = name
    print name + ' enters the room.'


def main():
    s = connect()
    users.append(s)
    names[s] = 'server'
    while True:
        r, w, e = select.select(users, [], [])
        for temp in r:
            if temp is s:
                newer(s)
            else:
                disconnect = False
                try:
                    data = temp.recv(1024)
                    if len(data) < 1:
                        disconnect = True
                    data = names[temp] + ': ' + data
                except socket.error:
                    disconnect = True
                if disconnect:
                    users.remove(temp)
                    del names[temp]
                else:
                    print data
                    for user in users:
                        if user != temp and user != s:
                            user.send(data)


if __name__ == '__main__':
    main()
