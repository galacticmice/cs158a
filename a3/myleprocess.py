import json
from socket import AF_INET, SOCK_STREAM, socket
from threading import Event, Thread
from typing import Any, Dict, Literal
from uuid import UUID, uuid4


class Message:
    def __init__(self, uuid: UUID = uuid4(), flag: Literal[0, 1] = 0) -> None:
        self._uuid: UUID = uuid
        self._flag: Literal[0, 1] = flag

    def getUUID(self) -> UUID:
        return self._uuid

    def getFlag(self) -> int:
        return self._flag

    def setFlag(self):
        self._flag = 1

    def exportDict(self) -> Dict[str, Any]:
        export: Dict[str, Any] = {"uuid": str(self._uuid), "flag": self._flag}
        return export

    @classmethod
    def importDict(cls, data: Dict[str, Any]) -> "Message":
        return cls(uuid=UUID(data["uuid"]), flag=data["flag"])


# do I store UUID or message class?
SERVERNAME = "localhost"
SERVERPORT = 12000
candidate: Message = Message()
t: Thread


def accept(callback, cSock, shutdown_event):
    global candidate
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", SERVERPORT))
    serverSocket.listen(1)
    print("Server is ready to connect.\n")
    try:
        conn, addr = serverSocket.accept()
        serverSocket.close()  # close listening socket
        conn.settimeout(1)
        while candidate.getFlag() == 0 and not shutdown_event.is_set():
            try:
                receivedBuffer = conn.recv(256)
                # if connection closed by previous neighbor
                if not receivedBuffer:
                    break

                # deserialize message
                receivedCandidate = Message.importDict(
                    json.loads(receivedBuffer.decode())
                )
                # if received id is the same as my holding candidate, leader is found
                if receivedCandidate.getUUID() == candidate.getUUID():
                    candidate.setFlag()
                # if received id is larger than my candidate, replace mine
                elif receivedCandidate.getUUID() > candidate.getUUID():
                    candidate = receivedCandidate
                # else+finally, send my results to next node
                callback(json.dumps(candidate.exportDict()))
            except socket.timeout:
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        serverSocket.close()
        conn.close()


if __name__ == "__main__":
    shutdown_event = Event()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((SERVERNAME, SERVERPORT))
        print("Connection established with forward neighbor.\n")
        forward = lambda message: clientSocket.send(message.encode())
        t = Thread(target=accept, args=(forward, clientSocket, shutdown_event))
        t.start()
        while t.is_alive():
            t.join(timeout=1)
    except KeyboardInterrupt:
        print("Program Interrupted, shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutdown_event.set()
        clientSocket.close()
        t.join()

# open client socket -
# create lambda function to send uuid to server -
# create server thread, passing lambda function as argument -
# in server, use while loop to wait for data
# if data received, compare with candidate
# how to know the end?? --> when to flip flag?
# call lambda function, sending candidate uuid
# when to end?
