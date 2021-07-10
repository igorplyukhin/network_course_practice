import socket
import sys

MAX_PORT_COUNT = 65535


def tcp_connect(ip, port, delay, output):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.settimeout(delay)
    try:
        tcp_socket.connect((ip, port))
        output.append(port)
    except:
        pass


if __name__ == '__main__':
    host = sys.argv[1]
    output = []
    for port in range(MAX_PORT_COUNT):
        tcp_connect(host, port, 1, output)

    print("Opened TCP ports:\n" + '\n'.join(map(str, output)))
