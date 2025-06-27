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
    connectionSocket.settimeout(1.0)
    try:
        while not stop_event.is_set():
            try:
                message = connectionSocket.recv(1024).decode()
            except timeout:
                continue

            # if exit -> close socket, remove from dict, end thread
            if message == "exit":
                with lock:
                    del sockets[my_addr]
                break

            modified = f"{my_addr}: {message}"
            # iterate through dict and propagate message to other clients
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


# override signals to join threads while in use
def handle_signals(signum, frame):
    stop_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTSTP, handle_signals)

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", SERVERPORT))
    serverSocket.listen(10)
    serverSocket.settimeout(1.0)
    print("Server is ready to connect.\n")

    while not stop_event.is_set():
        try:
            connectionSocket, addr = serverSocket.accept()
        except timeout:  # break listening loop when signal received
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
    print("Program exited gracefully.\n")


# server listens for connections
# opens port for new connection
# prints "New connection from (ip, port)"
# waits for buffer from opened connections
# process message
# if 'exit' --> close connection
# else --> prints message to all other connected clients
# printing
# - iterate list?
# - hashset?
# do i need locks?
# edge case: only 1 connected client --> if clientCount == 1
