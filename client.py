import socket
import select
import threading


def connect():
    s = socket.socket()
    s.connect(('localhost', 2333))
    return s


def listen(s):
    while True:
        r, w, e = select.select([s], [], [])
        if s in r:
            data = s.recv(1024)
            print data


def chat(s):
    while True:
        data = raw_input()
        s.send(data)


def main():
    s = connect()
    thread_listen = threading.Thread(target=listen, args=(s,))
    thread_listen.start()
    thread_chat = threading.Thread(target=chat, args=(s,))
    thread_chat.start()


if __name__ == '__main__':
    main()