import json
import time
from json import JSONDecodeError


class Cache():
    A = {}
    AAAA = {}
    NS = {}
    PTR = {}

    ITERATOR = ["A", "AAAA", "NS", "PTR"]
    CACHE_UPDATE_FREQ = 60  # seconds
    LAST_TIME_CACHE_UPDATED = time.time()
    CACHE_FOLDER = "./cache"

    def add_records(self, records: list) -> None:
        for record in records:
            ttl = record.ttl
            rdata = str(record.rdata)
            domain = str(record.rname)
            insertion_time = time.time()
            r_type = record.rtype
            if r_type == 1:  # A
                self.A[domain] = (rdata, insertion_time, ttl)
            elif r_type == 28:  # AAAA
                self.AAAA[domain] = (rdata, insertion_time, ttl)
            elif r_type == 2:  # NS
                self.NS[domain] = (rdata, insertion_time, ttl)
            elif r_type == 12:  # PTR
                self.PTR[domain] = (rdata, insertion_time, ttl)

    def remove_expired_records(self):
        self.LAST_TIME_CACHE_UPDATED = time.time()
        for d_name in self.ITERATOR:
            d = getattr(self, d_name)
            for k in list(d):
                v = d[k]
                if time.time() - v[1] > v[2]:
                    try:
                        d.pop(k)
                    except KeyError:
                        pass

    def serialize(self):
        for d_name in self.ITERATOR:
            d = getattr(self, d_name)
            with open(f"{self.CACHE_FOLDER}/{d_name}.json", "w") as f:
                f.write(json.dumps(d))

    def init(self):
        for d_name in self.ITERATOR:
            try:
                with open(f"{self.CACHE_FOLDER}/{d_name}.json", "r") as f:
                    setattr(self, d_name, json.loads(f.read()))
            except JSONDecodeError:
                pass
