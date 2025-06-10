import os
from socket import AF_INET, SOCK_STREAM, socket

N = 2
serverPort = 12000


def parse_message(message):
    msg_len = int(message[:N])
    processed_string = message[N:].upper()
    print(f"Message Length: {msg_len}")
    print(f"Processed String: {processed_string}")
    return processed_string


if __name__ == "__main__":
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print("Server is ready to receive")

    while True:
        # try cleanup zombie processes
        try:
            while True:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
        except ChildProcessError:
            pass

        connectionSocket, addr = serverSocket.accept()

        # if child, close listen socket
        if os.fork() == 0:
            serverSocket.close()

            message = connectionSocket.recv(64).decode()
            capSentence = parse_message(message)

            connectionSocket.send(capSentence.encode())
            print(f"Message Length Sent: {len(capSentence)}")
            connectionSocket.close()
            print("Connection Closed")
            os._exit(0)
        # if parent, close connection socket to remain listen-only, need to implement fork cleanup
        else:
            connectionSocket.close()
