import random

SEEDS = [
    b"CONNECT|EV01|1|0",
    b"AUTH|EV01|0|0",
    b"START|EV01|1|22",
    b"STOP|EV01|1|0",
    b"EMERGENCY|EV01|1|0",
    b"START||||",
]


def mutate(seed: bytes, rng: random.Random) -> bytes:
    value = bytearray(seed)
    operation = rng.randrange(5)
    if operation == 0:
        value.extend(bytes(rng.randrange(256) for _ in range(rng.randrange(1, 64))))
    elif operation == 1 and value:
        value[rng.randrange(len(value))] = rng.randrange(256)
    elif operation == 2:
        value = bytearray(b"A" * rng.randrange(0, 320))
    elif operation == 3:
        value = bytearray(seed.replace(b"|", b"||||"))
    else:
        value = bytearray(seed + b"|" + str(rng.randrange(-100000, 100000)).encode())
    return bytes(value)
