from struct import unpack
import dnslib
import binascii
import dns.resolver



def handle(data):
    print(data)
    print(data.hex())
    packet = data
    d = dnslib.DNSRecord.parse(packet)
    name = d.questions[0].get_qname()
    print(name)
    #dns.resolver.resolve(name)


if __name__ == '__main__':
    a = dns.resolver.resolve("vk.com")
    print(a)