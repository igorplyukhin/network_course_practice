import sys
from concurrent.futures import ThreadPoolExecutor
import socket

MAX_PORT_COUNT = 65535


def tcp_connect(ip, port, delay, output, sock):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.settimeout(delay)
    try:
        tcp_socket.connect((ip, port))
        output.append(port)
    except:
        pass


def udp_connect(ip, port, delay, closed_ports, sock1):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        client.sendto("ping".encode(), (ip, port))
        sock1.settimeout(delay)
        response, _ = sock1.recvfrom(1024)
        port = int.from_bytes(response[50:52], byteorder='big')
        closed_ports.append(port)
    except socket.timeout:
        pass
    except socket.error:
        pass

    client.close()


def start_pool(target, ip, delay, icmp_sock):
    output = []
    with ThreadPoolExecutor(max_workers=5000) as executor:
        for port in range(MAX_PORT_COUNT):
            executor.submit(target, ip, port, delay, output, icmp_sock)

    if target == udp_connect:
        a = []
        for p in range(MAX_PORT_COUNT):
            if p not in output:
                a.append(p)
        print(a)
    else:
        print(output)


def main():
    host_ip = sys.argv[1]
    delay = 1
    icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    start_pool(tcp_connect, host_ip, delay, None)
    start_pool(udp_connect, host_ip, delay, icmp_sock)


if __name__ == "__main__":
    main()
