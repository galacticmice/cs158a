from socket import socket, AF_INET, SOCK_STREAM, timeout
import threading
from typing import Dict, List
import signal

SERVERPORT = 12000
sockets: Dict[int, socket] = {}
threads: List[threading.Thread] = []
lock = threading.Lock()
stop_event = threading.Event()


def connected(stop_event, connectionSocket, my_addr):
    connectionSocket.settimeout(1.0)  # timer to periodically check for halt event
    try:
        while not stop_event.is_set():  # if halted, stop loop
            try:
                message = connectionSocket.recv(1024).decode()
            except timeout:
                continue

            # if exit received -> remove from dict, end thread
            if message == "exit":
                with lock:
                    del sockets[my_addr]
                break

            # setup chat structure, iterate through dict and propagate message to other clients
            modified = f"{my_addr}: {message}"
            with lock:
                for addr, sock in sockets.items():
                    if addr != my_addr:
                        sock.sendall(modified.encode())
    except Exception as e:  # if connection dropped
        print(f"{my_addr}: {e}")
    finally:  # remove socket whenever thread ends(forcefully or normally)
        with lock:
            if my_addr in sockets:
                del sockets[my_addr]
        connectionSocket.close()


def handle_signals(signum, frame):  # override signals to join threads while in use
    stop_event.set()


if __name__ == "__main__":
    # override ctrl-z/c signals
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTSTP, handle_signals)

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", SERVERPORT))
    serverSocket.listen(10)
    serverSocket.settimeout(1.0)
    print("Server is ready to connect.\n")

    # timer to periodically check for server close command
    while not stop_event.is_set():
        try:
            connectionSocket, addr = serverSocket.accept()
        except timeout:
            continue
        print(f"{addr} Accepted connection. \n")
        t = threading.Thread(
            target=connected, args=(stop_event, connectionSocket, addr)
        )
        t.start()
        with lock:
            sockets[addr] = connectionSocket
            threads.append(t)

    # join all stopped threads and close socket
    with lock:
        for t in threads:
            t.join()
    serverSocket.close()
    print("\nProgram exited gracefully.\n")
