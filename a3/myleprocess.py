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


FW_SERVER_IP = None
FW_SERVER_PORT = None
MY_SERVER_IP = None
MY_SERVER_PORT = None
candidate: Message = Message()


def accept(callback, cSock, shutdown_event, log):
    global candidate
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((MY_SERVER_IP, MY_SERVER_PORT))
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

                # if received id is the same as my holding candidate, leader is found and send
                if receivedCandidate.getUUID() == candidate.getUUID():
                    candidate.setFlag()  # leader found, set flag = 1
                    log_received(log, receivedCandidate)
                    log.write(f"Leader is decided to {candidate.getUUID()}.\n")
                    callback(json.dumps(candidate.exportDict()))  # announce
                    log_sent(log)
                # if received id is larger than my candidate, replace mine and send
                elif receivedCandidate.getUUID() > candidate.getUUID():
                    candidate = receivedCandidate  # replace my candidate
                    callback(json.dumps(candidate.exportDict()))  # announce
                    log_sent(log)
                # else if received is smaller, drop
                else:
                    log_received(log, receivedCandidate, "greater")
                    log.write("Received message is smaller: dropped...\n")
            except socket.timeout:  # periodically check for shutdowns
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        serverSocket.close()
        conn.close()


def log_sent(log):
    log.write(f"Sent: uuid={candidate.getUUID()}, flag={candidate.getFlag()}\n")


def log_received(log, o, eval="equal"):
    log.write(
        f"Received: uuid={o.getUUID()}, flag={o.getFlag()}, {eval}, {candidate.getFlag()}\n"
    )


def read_config(config):
    lines = config.readlines()
    MY_SERVER_IP, MY_SERVER_PORT = lines[0].strip().split(",")
    FW_SERVER_IP, FW_SERVER_PORT = lines[1].strip().split(",")


if __name__ == "__main__":
    config = open("config.txt", "r")
    read_config(config)
    log = open("log.txt", "w")
    shutdown_event = Event()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((FW_SERVER_IP, FW_SERVER_PORT))
        print("Connection established with forward neighbor.\n")
        forward = lambda message: clientSocket.send(message.encode())
        forward(candidate.exportDict())  # send my first candidate
        print("Sent first candidate.\n")
        log_sent(log)
        t = Thread(target=accept, args=(forward, clientSocket, shutdown_event, log))
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
        config.close()
        log.close()
