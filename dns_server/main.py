import socket
import time
import random as rnd
from Cache import Cache
from dnslib import DNSRecord, QTYPE, RR, A, AAAA, NS, PTR

IP = '127.0.0.1'
PORT = 53

ROOT_SERVER_IP = "192.203.230.10"
EXTRA_ROOT_SERVERS = ["192.33.4.12", "199.7.91.13", "192.5.5.241"]

CACHE = Cache()


def resolve(request: bytes) -> bytes:
    ip = ROOT_SERVER_IP
    byte_response = None
    response = None
    while response is None or len(response.rr) == 0:
        request_obj = DNSRecord.parse(request)
        cache_record = look_up_in_cache(request_obj)
        if cache_record:
            return cache_record
        try:
            byte_response = request_obj.send(ip, timeout=4)
        except socket.timeout:
            ip = EXTRA_ROOT_SERVERS[rnd.randint(0, len(EXTRA_ROOT_SERVERS) - 1)]
            continue
        response = DNSRecord.parse(byte_response)
        if response.header.rcode == 3:  # Domain name does not exist
            return byte_response
        CACHE.add_records(response.ar)
        ip = get_1st_ipv4_address_in_additional_records(response)
        if ip == -1 and len(response.rr) == 0:  # Case server responds with NS record for PTR request
            resp = resolve(DNSRecord.question(str(response.auth[0].rdata)).pack())
            n = DNSRecord.parse(resp)
            ip = get_ip_from_response(n)
    CACHE.add_records(response.rr)
    return byte_response


def look_up_in_cache(request_obj):
    domain = str(request_obj.q.qname)
    q_type = request_obj.q.qtype
    if q_type == 1 and domain in CACHE.A.keys():  # A type
        return form_ans(request_obj, RR(domain, QTYPE.A, rdata=A(CACHE.A[domain][0]), ttl=60))
    elif q_type == 28 and domain in CACHE.AAAA.keys():  # AAAA type
        return form_ans(request_obj, RR(domain, QTYPE.AAAA, rdata=AAAA(CACHE.AAAA[domain][0]), ttl=60))
    elif q_type == 2 and domain in CACHE.NS.keys():  # NS type
        return form_ans(request_obj, RR(domain, QTYPE.NS, rdata=NS(CACHE.NS[domain][0]), ttl=60))
    elif q_type == 12 and domain in CACHE.PTR.keys():  # PTR type
        return form_ans(request_obj, RR(domain, QTYPE.PTR, rdata=PTR(CACHE.PTR[domain][0]), ttl=60))

    return None


def form_ans(request_obj, rr) -> bytes:
    a = request_obj.reply()
    a.add_answer(rr)
    return a.pack()


def get_1st_ipv4_address_in_additional_records(response):
    return next((str(x.rdata) for x in response.ar if x.rtype == 1), -1)


def get_ip_from_response(response):
    return str(response.rr[0].rdata)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    CACHE.init()
    CACHE.remove_expired_records()
    while True:
        data, addr = sock.recvfrom(512)
        if time.time() - CACHE.LAST_TIME_CACHE_UPDATED > Cache.CACHE_UPDATE_FREQ:
            CACHE.remove_expired_records()
        r = resolve(data)
        sock.sendto(r, addr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        CACHE.serialize()
