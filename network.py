import sys
import socket
import threading
from time import sleep

def thread(con, connections):
    while True:
        event = con.recv(1024)
        event = event.decode('utf-8')
        fields = event.split('|')
        type = fields[0]
        sleep(1)
        if type == 'send':
            connections[fields[2]].send(event.encode('utf-8'))
            for key, value in connections.items():
                if fields[2] != key:
                    value.send(event.encode('utf-8'))
        elif type == 'release':
            for key, value in connections.items():
                if fields[1] != key:
                    value.send(event.encode('utf-8'))
        elif type == 'reply':
            connections[fields[1]].send(event.encode('utf-8'))

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 65432))
    s.listen()

    connections = {}

    while True:
        con, addr = s.accept()
        pid = con.recv(1024)
        pid = pid.decode('utf-8')
        connections[pid] = con
        # print(connections)
        threading.Thread(target = thread, args=[con, connections]).start()
        # fields = event.split('|')
        # addr = ('127.0.0.1', process[fields[2]])
        # s.sendto(event.encode('utf-8'), addr)


if __name__ == '__main__':
    main()
