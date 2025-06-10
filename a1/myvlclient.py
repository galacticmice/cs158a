import re
from socket import AF_INET, SOCK_STREAM, socket

serverName = "localhost"
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sentence = None

while True:
    sentence = input("Input [00-99] followed by message(no spaces): ")
    match = re.search(r"^[0-9]{2}", sentence)
    if match:
        break
    else:
        print("Invalid input. Please try again.")
        continue

clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(64).decode()
print("From Server:", modifiedSentence)

clientSocket.close()
