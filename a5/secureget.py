from socket import socket, AF_INET, SOCK_STREAM
from ssl import create_default_context

HOST_ADDRESS = "www.google.com"
HOST_PORT = 443

if __name__ == "__main__":
    with socket(AF_INET, SOCK_STREAM) as sock:
        print("TCP socket created")
        sock.connect((HOST_ADDRESS, HOST_PORT))
        print("Connected to server")
        with create_default_context().wrap_socket(
            sock, server_hostname=HOST_ADDRESS
        ) as ssock:
            print("SSL wrap complete")
            request = (
                f"GET / HTTP/1.1\r\nHost: {HOST_ADDRESS}\r\nConnection: close\r\n\r\n"
            )
            ssock.sendall(request.encode("utf-8"))
            print("Sent HTTP GET request: \n")
            print(f"----------HTTP GET----------\n{request}")

            with open("response.html", "w") as file:
                count = 1
                split = False
                header = None
                while True:
                    buff = ssock.recv(4096)
                    if not buff:
                        break
                    if not split:
                        sep = buff.find(b"\r\n\r\n")
                        if sep != 1:
                            split = True
                            header = buff[:sep].decode("utf-8")
                            file.write(buff[sep + 4 :].decode("utf-8"))
                        else:
                            header += buff.decode("utf-8")
                    else:
                        file.write(buff.decode("utf-8"))

                print("---------HTTP REPLY---------")
                print(header)
