import sys
import socket
import queue
import threading

def receiving(s, requests, replies):
    while True:
        event, addr = s.recv(1024)
        event = event.decode('utf-8')
        fields = event.split('|')
        type = fields[0]
        if type == 'send':
            requests.put((type, fields[1], fields[2], fields[3]))
            #chain.append((fields[1], fields[2], fields[3]))
        else:
            replies.put((type, fields[1], fields[2]))

def processing(s, pid, requests, replies, chain):
    while True:
        while not requests.empty():
            request = requests[0]
            if request[2] == pid: # this process requests access to resource
                while replies.empty():
                    pass
                while not replies.empty() and replies[0][1] == pid and requests[0][2] == pid: # broadcast only if replies are received
                    replies.get()
                    requests.get()
                s.send('release|{1}'.format(pid).encode('utf-8')) # release resource from this process
                chain[0]-=request[3]
                chain.append((request[1], request[2], request[3]))
            else: # another process requests access to resource
                s.send('reply|{0}'.format(request[2])) # reply to process requesting
                while replies.empty():
                    pass
                if replies[0][1] == request[2]: # release signal from same process as broadcast
                    if request[1] == pid:
                        chain[0]+=request[3]
                    chain.append((request[1], request[2], request[3]))
                    requests.get()
                    replies.get()


def main():
    # python server.py port pid
    port = int(sys.argv[1])
    pid = sys.argv[2]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))

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
            s.send(cmd.encode('utf-8'))

if __name__ == '__main__':
    main()
