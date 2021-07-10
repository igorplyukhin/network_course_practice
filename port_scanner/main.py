import asyncio
from random import SystemRandom
import socket

def run(tasks, *, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    # waiting for all tasks
    return loop.run_until_complete(asyncio.wait(tasks))


async def a(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result


async def scanner(ip, port, loop=None):
    fut = asyncio.open_connection(ip, port, loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=1)  # This is where it is blocking?
        print("{}:{} Connected".format(ip, port))
    except asyncio.TimeoutError:
        pass
    # handle connection refused and bunch of others
    except Exception as exc:
        print('Error {}:{} {}'.format(ip, port, exc))


def scan(ips, ports, randomize=False):
    loop = asyncio.get_event_loop()
    if randomize:
        rdev = SystemRandom()
        ips = rdev.shuffle(ips)
        ports = rdev.shuffle(ports)

    # let's pass list of task, not only one
    run([scanner(ip, port) for port in ports for ip in ips])


ips = ["127.0.0.1"]
ports = [x for x in range(630, 65535)]
scan(ips, ports)
