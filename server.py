import socket

word_len = 65
def popcount(x):
    if x == 0: 
        return 0
    return (x & 1) + popcount(x >> 1)

def encoding_word(x):
    y = x
    for i in range(word_len):
        bit = 0
        if(y & (1 << i)):
            bit = 1
        if(bit):
            for len in range(8):
                sz = 1 << len
                y ^= 1 << (word_len + (i // sz) % 2 + 2 * len)
    return y

def decoding_word(x):
    nx = x
    for i in range(15):
        if nx & (1 << (word_len + i)):
            nx ^= 1 << (word_len + i)
    y = nx
    nx = encoding_word(nx)
    if(nx == x):
        return 0
    if popcount(x ^ nx) == 1:
        return 1
    mask = (1 << word_len) - 1
    for i in range(15):
        curmask = 0
        if (nx & (1 << (i + word_len))) != (x & (1 << (i + word_len))):
            len = 1 << (i // 2)
            for pos in range(i % 2 * len, word_len, 2 * len):
                for j in range(len):
                    curmask |= 1 << (pos + j)
            mask &= curmask
    y ^= mask
    y = encoding_word(y)
    if(popcount(y^x) == 1):
        return 1
    return 2

def decoding_arr(data):
    cnt = [0, 0, 0]
    for x in data:
        cnt[decoding_word(x)] += 1
    return cnt

def readexactly(conn, bytes_count):

    b = b''
    while len(b) < bytes_count: 
        part = conn.recv(bytes_count - len(b)) 
        if not part:
            raise IOError("Connection lost")
        b += part
    return b

def read(conn):

    res = []
    while True:
        part_len = int.from_bytes(readexactly(conn, 2), "big")
        if part_len == 0:
            return res
        res.append(int.from_bytes(readexactly(conn, part_len), "big"))
    return res



server = socket.socket()
server.bind(('localhost', 9090))
server.listen(1)
while True:
    conn, addr = server.accept()
    print('connected:', addr)
    data = read(conn)
    print("decoding start")
    ncnt = decoding_arr(data)
    print("send result", ncnt)
    conn.send(str(ncnt).encode())
    conn.close()

