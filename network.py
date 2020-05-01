import sys
import socket
import threading
from time import sleep

def thread(con, events):
    while True:
        event = con.recv(1024)
        event = event.decode('utf-8')
        fields = event.split('|')
        type = fields[0]
        sleep(1)
        if type == 'send':
            for key, value in connections:
                if fields[2] != key:
                    value.send(event)
                    connections[fields[2]].send(event)
        elif type == 'release':
            for key, value in connections:
                if fields[1] != key:
                    value.send(event)
                    connections[fields[1]].send(event)
        elif type == 'reply':
            connections[fields[1]].send(event)

def main():
    # python network.py port1 pid1 port2 pid2 port3 pid3
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 65432))
    s.listen()

    ports = {
        int(sys.argv[1]): sys.argv[2],
        int(sys.argv[3]): sys.argv[4],
        int(sys.argv[5]): sys.argv[6]
    }

    connections = {}

    print(ports)

    while True:
        con, addr = s.accept()
        connections[ports[addr[1]]] = con
        threading.Thread(target = thread, args=[con, events]).start()
        # fields = event.split('|')
        # addr = ('127.0.0.1', process[fields[2]])
        # s.sendto(event.encode('utf-8'), addr)


if __name__ == '__main__':
    main()
