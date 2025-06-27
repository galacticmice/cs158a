from socket import socket, AF_INET, SOCK_STREAM, timeout
import threading
import signal

SERVERNAME = "localhost"
SERVERPORT = 12000
STOP_COMMAND = "exit"


def receive(stop_event, clientSocket):
    clientSocket.settimeout(1.0)
    while not stop_event.is_set():
        try:
            received = clientSocket.recv(1024).decode()
        except timeout:
            continue

        if received == "":
            print("Disconnected from server")
            stop_event.set()
            continue

        print(received)


def send(stop_event, clientSocket):
    while not stop_event.is_set():
        sentence = input()

        clientSocket.send(sentence.encode())
        if sentence == STOP_COMMAND:
            break
    return


def handle_signals(signum, frame):
    stop_event.set()


if __name__ == "__main__":
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
