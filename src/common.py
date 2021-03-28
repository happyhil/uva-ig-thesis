import hashlib


def __hash(value, n=8):
    return int(hashlib.sha256(value.encode('utf-8')).hexdigest(), 16) % 10**8
    