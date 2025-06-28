from socket import socket, AF_INET, SOCK_STREAM, timeout
import threading
import signal

SERVERNAME = "localhost"
SERVERPORT = 12000
STOP_COMMAND = "exit"


def receive(stop_event, clientSocket):
    # periodically set timer to check if client was force closed
    clientSocket.settimeout(1.0)
    while not stop_event.is_set():
        try:
            received = clientSocket.recv(1024).decode()
        except timeout:
            continue

        # if client was closed by server, start shutdown process
        if received == "":
            print("Disconnected from server")
            stop_event.set()
            continue

        # otherwise, print message received
        print(received)


def send(stop_event, clientSocket):
    # periodically check if client was force closed by user (bypass input block)
    clientSocket.settimeout(1.0)
    while not stop_event.is_set():
        try:
            sentence = input()
        except timeout:
            continue
        clientSocket.send(sentence.encode())
        if sentence == STOP_COMMAND:  # if user sends "exit", start pre-cleanup
            break


def handle_signals(signum, frame):
    stop_event.set()


if __name__ == "__main__":
    # handle ctrl-z/c signals
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTSTP, handle_signals)
    stop_event = threading.Event()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((SERVERNAME, SERVERPORT))
        print("Connected Successfully!")
    except OSError as e:
        print(f"Connection failed: {e}")

    receive_t = threading.Thread(target=receive, args=(stop_event, clientSocket))
    receive_t.start()
    send_t = threading.Thread(target=send, args=(stop_event, clientSocket))
    send_t.start()

    receive_t.join()
    send_t.join()
    clientSocket.close()
