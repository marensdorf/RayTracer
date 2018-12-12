"""
Code taken from:
https://laszukdawid.com/2017/02/04/halton-sequence-in-python/
"""


def is_prime(num):
    """Checks if num is a prime value"""
    for i in range(2, int(num ** 0.5) + 1):
        if (num % i) == 0: return False
    return True


def next_prime():
    prime = 3
    while 1:
        if is_prime(prime):
            yield prime
        prime += 2


def vdc(n, base=2):
    v, denom = 0, 1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        v += remainder / float(denom)
    return v


def halton_sequence(size, dim):
    seq = []
    primeGen = next_prime()
    next(primeGen)
    for d in range(dim):
        base = next(primeGen)
        seq.append([vdc(i, base) for i in range(size)])
    return seq
