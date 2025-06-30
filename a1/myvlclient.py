import re
from socket import AF_INET, SOCK_STREAM, socket

serverName = "localhost"
serverPort = 12000
BUFSIZE = 64
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sentence = None

while True:
    sentence = input("Input [00-99] followed by message(no spaces): ")
    # validate input with regex
    match = re.search(r"^[0-9]{2}", sentence)
    if match:
        break
    else:
        print("Invalid input. Please try again.\n")
        continue

length = len(sentence)
remaining = length
while remaining > 0:
    bufSentence = sentence[:64]
    sentence = sentence[64:]
    clientSocket.send(bufSentence.encode())
    remaining -= BUFSIZE


modifiedSentence = ""
while length > 0:
    modifiedSentence += clientSocket.recv(BUFSIZE).decode()
    length -= 64


print("From Server:", modifiedSentence)
clientSocket.close()
