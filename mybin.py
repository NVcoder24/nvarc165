def dec_to_bin(a:int):
    return str(bin(a))[2:]

def bin_to_dec(a:str):
    b = a[::-1]
    r = 0
    for i in range(len(a)):
        if b[i] == "1": r += 2 ** i
    return r

def bin_lim(a:int, n:int):
    if a > 2 ** n - 1:
        return 2 ** n - 1
    return a

def bin_8_lim(a:int):
    return bin_lim(a, 8)

def bin_16_lim(a:int):
    return bin_lim(a, 16)

def bin_ext(a:int, n:int):
    b = dec_to_bin(bin_lim(a, n))
    c = ""
    for i in range(n - len(b)):
        c += "0"
    return c + b

def bin_8_ext(a:int):
    return bin_ext(a, 8)

def bin_16_ext(a:int):
    return bin_ext(a, 16)

def bin_sum(a:int, b:int, n:int):
    r = a + b
    if r > 2 ** n - 1:
        r = r - (2 ** n - 1)
        return r, 1
    return r, 0

def bin_16_sum(a:int, b:int):
    return bin_sum(a, b, 16)

def bin_sub(a:int, b:int, n:int):
    r = a - b
    if r < 0:
        r = -r
        return r, 1
    return r, 0

def bin_16_sub(a:int, b:int):
    return bin_sub(a, b, 16)

def bin_shl(a:int, n:int):
    b = list(bin_ext(a, n))
    b.append(b[0])
    b.pop(0)
    return bin_to_dec(b)

def bin_8_shl(a:int):
    return bin_shl(a, 8)

def bin_16_shl(a:int):
    return bin_shl(a, 16)

def bin_shr(a:int, n:int):
    b = list(bin_ext(a, n))
    b.insert(0, b[-1])
    b.pop()
    return bin_to_dec(b)

def bin_8_shr(a:int):
    return bin_shr(a, 8)

def bin_16_shr(a:int):
    return bin_shr(a, 16)

def bin_16_8_split(a:int):
    b = bin_ext(a, 16)
    return bin_to_dec(b[0:8]), bin_to_dec(b[8:16])

def bin_8_16_comp(a:int, b:int):
    return bin_to_dec(bin_8_ext(a) + bin_8_ext(b))

def bin_not(a:int, n:int):
    r = ""
    for i in bin_ext(a, n):
        if i == "1":
            r += "0"
        else:
            r == "1"
    return bin_to_dec(r)

def bin_and(a:int, b:int, n:int):
    r = ""
    for i, j in zip(bin_ext(a, n), bin_ext(b, n)):
        if i == "1" and j == "1":
            r += "1"
        else:
            r += "0"
    return bin_to_dec(r)

def bin_or(a:int, b:int, n:int):
    r = ""
    for i, j in zip(bin_ext(a, n), bin_ext(b, n)):
        if i == "1" or j == "1":
            r += "1"
        else:
            r += "0"
    return bin_to_dec(r)

def bin_xor(a:int, b:int, n:int):
    r = ""
    for i, j in zip(bin_ext(a, n), bin_ext(b, n)):
        if (i == "1" and j == "0") or (i == "0" and j == "1"):
            r += "1"
        else:
            r += "0"
    return bin_to_dec(r)

def bin_16_not(a:int):
    return bin_not(a, 16)

def bin_16_and(a:int, b:int):
    return bin_and(a, b, 16)

def bin_16_or(a:int, b:int):
    return bin_or(a, b, 16)

def bin_16_xor(a:int, b:int):
    return bin_xor(a, b, 16)