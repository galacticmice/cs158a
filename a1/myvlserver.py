import os
from socket import AF_INET, SOCK_STREAM, socket

N = 2
serverPort = 12000


def parse_message(message, addr):
    msg_len = int(message[:N])
    processed_string = message[N:]
    print(f"{addr} Message Length: {msg_len}")
    print(f"{addr} Processed String: {processed_string}")
    return processed_string.upper()


if __name__ == "__main__":
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print("Server is ready to receive.\n")

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
        print(f"{addr} Accepted connection")

        # if child, close listen socket, only use accept socket, remember to exit
        if os.fork() == 0:
            serverSocket.close()

            message = connectionSocket.recv(64).decode()
            capSentence = parse_message(message, addr)

            connectionSocket.send(capSentence.encode())
            print(f"{addr} Message Length Sent: {len(capSentence)}")
            connectionSocket.close()
            print(f"{addr} Connection closed")
            os._exit(0)
        # if parent, close connection socket to remain listen-only, need to implement fork cleanup
        else:
            connectionSocket.close()
