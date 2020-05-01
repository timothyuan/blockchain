import sys
import socket
import queue
import threading

def receiving(s, requests, replies):
    while True:
        event = s.recv(1024)
        event = event.decode('utf-8')
        fields = event.split('|')
        type = fields[0]
        if type == 'send':
            requests.put((type, fields[1], fields[2], fields[3]))
            #chain.append((fields[1], fields[2], fields[3]))
        elif type == 'release' or type == 'reply':
            replies.put((type, fields[1]))

def processing(s, pid, requests, replies, chain):
    while True:
        while not requests.empty():
            request = requests.get()
            if request[2] == pid: # this process requests access to resource
                while replies.empty():
                    pass
                reply1 = replies.get()
                reply2 = replies.get()
                if not reply1[1] == pid or not reply2[1] == pid:
                    print('invalid reply')
                s.send('release|{0}'.format(pid).encode('utf-8')) # release resource from this process
                chain[0]-=int(request[3])
                chain.append((request[1], request[2], request[3]))
            else: # another process requests access to resource
                s.send('reply|{0}'.format(request[2]).encode('utf-8')) # reply to process requesting
                while replies.empty():
                    pass
                reply = replies.get()
                if reply[1] == request[2]: # release signal from same process as broadcast
                    if request[1] == pid:
                        chain[0]+=int(request[3])
                    chain.append((request[1], request[2], request[3]))


def main():
    # python server.py port pid
    pid = sys.argv[1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 65432))
    s.send(pid.encode('utf-8'))

    requests = queue.Queue()
    replies = queue.Queue()
    chain = [10]

    threading.Thread(target = receiving, args=[s, requests, replies]).start()
    threading.Thread(target = processing, args=[s, pid, requests, replies, chain]).start()
    while True:
        cmd = input('Enter transaction (e for examples, p to print balance, c to print blockchain): ')
        if cmd =='e':
            print('send|to|from|amount')
            print('send|P1|P2|2')
            continue
        elif cmd =='p':
            print(chain[0])
        elif cmd =='c':
            print(chain[1:])
        else:
            fields = cmd.split('|')
            if int(fields[3])>chain[0]:
                print('insufficient balance')
            else:
                s.send(cmd.encode('utf-8'))

if __name__ == '__main__':
    main()
