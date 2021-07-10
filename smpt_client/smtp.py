import base64
import mimetypes
import socket
import ssl
from conf import *


def _2b64(s) -> str:
    return base64.b64encode(s.encode() if type(s) is str else s).decode()


def _2q_encoded(s) -> str:
    return f"=?utf-8?B?{_2b64(s)}?="


boundary = '----==--bound.1262885.sas1-e05fd3bc78f9.qloud-c.yandex.net'

global_headers = {
    "From": f'"ABob Example" <{sender}>',
    "Subject": _2q_encoded(subject),
    "MIME-Version": "1.0",
    "Content-Type": f'multipart/mixed;\r\n\t boundary="{boundary}"'}

msg_headers = {"Content-Type": "text/plain"}

pic_headers = {"Content-Disposition": "",
               "Content-Transfer-Encoding": "base64",
               "Content-Type": "",
               }


def request(sock, req):
    sock.send((req + '\n').encode())
    recv_data = sock.recv(65535).decode()
    return recv_data


def dict2str(d):
    return "\n".join([f'{key}: {value}' for key, value in d.items()])


def format_letter(global_h, msg_h, msg):
    return f"{dict2str(global_h)}\n\n" \
           f"--{boundary}\n" \
           f"{dict2str(msg_h)}\n\n" \
           f"{msg}\n\n" \
           f"--{boundary}\n" \
           f"{attach_files(attachments)}\n" \
           f"\n--{boundary}--" \
           f"\n."


def attach_files(attachments) -> str:
    s = ''
    for f in attachments:
        filename = f';\n\tfilename="{_2q_encoded(f)}"'
        pic_headers["Content-Type"] = mimetypes.guess_type(f)[0] + filename
        pic_headers["Content-Disposition"] = f'attachment{filename}'
        with open(f'./attach/{f}', 'rb') as pic:
            s += f'{dict2str(pic_headers)}\n\n{_2b64(pic.read())}\n--{boundary}\n'
    return s


def read_message(filename) -> str:
    with open(filename, "r") as f:
        return ''.join(map(lambda x: '.' + x if x[0] == '.' else x, f.readlines()))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    client = ssl.wrap_socket(client)
    print(client.recv(1024))
    print(request(client, 'ehlo Ivan'))
    print(request(client, 'AUTH LOGIN'))
    print(request(client, _2b64(user_name)))
    print(request(client, _2b64(password)))
    print(request(client, f'MAIL FROM:{sender}'))
    print(request(client, f"RCPT TO:{receiver}"))
    print(request(client, 'DATA'))

    print(request(client, format_letter(global_headers, msg_headers, read_message("msg.txt"))))
