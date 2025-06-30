import os
from socket import AF_INET, SOCK_STREAM, socket

N = 2
serverPort = 12000
BUFSIZE = 64


def parse_message(message, addr):
    return message.upper()


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
            first_buf = connectionSocket.recv(BUFSIZE).decode()
            char_length = int(first_buf[:N])
            input_length = char_length + 2

            message = first_buf[N:]
            input_length -= BUFSIZE
            while input_length > 0:
                message += connectionSocket.recv(BUFSIZE).decode()
                input_length -= BUFSIZE

            print(f"{addr} Message Length: {char_length}")
            print(f"{addr} Processed String: {message}")

            capSentence = parse_message(message, addr)

            while char_length > 0:
                send_buffer = capSentence[:64]
                capSentence = capSentence[64:]
                connectionSocket.send(send_buffer.encode())
                char_length -= BUFSIZE

            print(f"{addr} Message Length Sent: {len(message)}")

            connectionSocket.close()
            print(f"{addr} Connection closed")
            os._exit(0)
        # if parent, close connection socket to remain listen-only, need to implement fork cleanup
        else:
            connectionSocket.close()
