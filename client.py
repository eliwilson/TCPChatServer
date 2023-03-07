# Usage "python client.py serverIP port"
# ex: "python client.py 10.129.86.134 12000"
# First two messages sent are username and number
# of channel to enter
# Subsequent messages will be sent to users in same
# channel
# "quit" to leave chat
from socket import *
from threading import Thread, Lock
import sys

# sends messages to server
def msgInput():
    while True:
        sentence = input()
        clientSocket.send(sentence.encode())
        if(sentence == "quit"):
            return

if __name__ == "__main__":
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    inputThread = Thread(target=msgInput, args=())
    inputThread.daemon = True
    inputThread.start()
    while(True):    # receives messages from server
        sentence = clientSocket.recv(1024).decode()
        print (sentence)
        if(sentence == "shutdown"):
            break
        
    clientSocket.close()
