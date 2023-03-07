# Usage "python server.py port numberOfChannels"
# ex: "python server.py 12000 5"
# Server Commands:
#   "users": prints names of all users
#   "stats": prints number of messages sent and received for all users
#   "quit": close server, exit program
from socket import *
from threading import *
import sys, os
import signal
from _thread import interrupt_main

class User:
    def __init__(self, name, socket, channel):
        self.name = name
        self.socket = socket
        self.channel = channel
        self.recd = 0
        self.sent = 0

mutex = Lock()
users = set()

# generates list of channels for user to choose one
def channelPrompt(numChannels):
    s = "\nEnter Channel ("
    for i in range(numChannels):
        if(i+1 != numChannels):
            s += str(i+1) + ", "
        else:
            s += "or " + str(i+1) + "): "
    return s
        
# creates string with list of users
# includes messages sent/received if stats == 1
def printUsers(stats):
    s = "\n"
    for i in users:
        s += i.name
        if(stats):
            s += ("\tsent: " + str(i.sent) + "\treceived: " + str(i.recd))
        s += "\n"
    return s

# sends shutdown message to clients and closes them
def shutdownUsers():
    for i in users:
        i.socket.send("shutdown".encode())
        i.socket.close()

# sends string msg to users in u's channel
def sendMsg(msg, u):
    for i in users:
        if(u != i and i.channel == u.channel):
            i.recd += 1
            i.socket.send(msg.encode())

# waits for and receives messages from client
def getMsg(user):
    while True:
        sentence = user.socket.recv(1024).decode()
        if(sentence == "quit"): # user exits server
            mutex.acquire()
            users.remove(user) # removes user from userlist
            mutex.release()
            user.socket.send("shutdown".encode()) # sends shutdown message to user
            user.socket.close()
            break
        else: # user sends message to server
            user.sent += 1
            s = user.name + ": " + sentence
            sendMsg(s, user)

# processes server commands
def serverInput():
    while True:
        s = input(">>")
        if(s == "users"):           # prints userlist
            users = printUsers(0)
            print(users)
        elif(s == "stats"):         # prints user stats
            users = printUsers(1)
            print(users)
        elif(s == "quit"):          # closes server
            shutdownUsers()
            os._exit(1)
            return

if __name__ == "__main__":
    numChannels = int(sys.argv[2])
    serverPort = int(sys.argv[1])
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen()
    print('The server is ready to receive')
    cmdThread = Thread(target=serverInput, args=())
    cmdThread.daemon = True
    cmdThread.start()
    while True:
        connectionSocket, addr = serverSocket.accept()

        # prompts client for username
        connectionSocket.send('Enter username:'.encode())
        sentence = connectionSocket.recv(1024).decode()
        #print("sentence:" + sentence)
        if(sentence == "quit"):
            connectionSocket.close()
            continue
        elif(sentence.isspace()):
            sentence = addr[0]
        
        # prompts client for channel to join
        s = channelPrompt(numChannels)
        connectionSocket.send(s.encode())
        channel = connectionSocket.recv(1024).decode()
        if(channel == "quit"):
            connectionSocket.close()
            continue
        
        u = User(sentence, connectionSocket, int(channel))
        
        mutex.acquire()
        users.add(u)
        mutex.release()
        
        #connectionSocket.send("\nname recd\n".encode())

        t1 = Thread(target=getMsg, args=(u,))
        t1.daemon = True
        t1.start()
