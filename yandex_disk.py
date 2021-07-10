import socket
import ssl
import base64
import hashlib


login = "login@yandex.ru"
passwd = "passwd"
server_addr = "webdav.yandex.ru"
auth = str(base64.b64encode(f"{login}:{passwd}".encode()))[2:-1]


def get_full_reply(sock: socket.socket, bufsize=65536):
    sock.settimeout(1)
    result = b""
    try:
        while True:
            data = sock.recv(bufsize)
            if not data:
                break
            result += data
    except socket.timeout:
        return result
    return result


def send_command(sock: socket.socket, command):
    sock.sendall(command.encode())
    return get_full_reply(sock)


def print_packet(packet: bytes):
    str_packet = packet.decode()
    for line in str_packet.split("\n"):
        print(line)
    print()


def get_file_from_disk(filename: str, sock: socket.socket):
    request = (
        f"GET /{filename} HTTP/1.1\n"
        f"Host: {server_addr}\n"
        f"Accept: */*\n"
        f"Authorization: Basic {auth}\n\n"
    )
    print(request)
    response = send_command(sock, request)
    print_packet(response)


def load_file_to_disk(filename: str, destination: str, sock: socket.socket):
    with open(filename, "rb") as file:
        data = file.read()

    md5 = hashlib.md5()
    md5.update(data)
    etag = md5.hexdigest()

    sha256 = hashlib.sha256()
    sha256.update(data)
    sha256_hash = sha256.hexdigest()
    request = (
        f"PUT /{destination} HTTP/1.1\n"
        f"Host: {server_addr}\n"
        f"Accept: */*\n"
        f"Authorization: Basic {auth}\n"
        f"Etag: {etag}\n"
        f"Sha256: {sha256_hash}\n"
        f"Expect: 100-continue\n"
        f"Content-Type: application/binary\n"
        f"Content-Length: {len(data)}\n\n"
    )
    print(request)
    response = send_command(sock, request)
    print_packet(response)
    if b"100" in response:
        data_packet = (
            f"{str(data)[2:-1]}\n\n"
        )
        print(data_packet)
        print_packet(send_command(sock, data_packet))


if __name__ == '__main__':
    with socket.create_connection((server_addr, 443)) as sock:
        sock = ssl.wrap_socket(sock)
        # get_file_from_disk("text.txt", sock)

        load_file_to_disk("image.jpg", "image.jpg", sock)
