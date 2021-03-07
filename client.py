import socket
import random
word_len = 65

def byte_to_origarr(data):
    bitarr = '' 
    for B in data:
        for i in range(8):
            if(B & (1 << i)):
                bitarr += '1'
            else: 
                bitarr += '0'
    res = []
    for word in (bitarr[_:_ + word_len] for _ in range(0, len(bitarr), word_len)):
        x = 0
        for i in range(len(word)):
            x |= int(word[i] == '1') << i
        res.append(x)
    return res

#def origarr_to_byte(bitarr):
    #res = []
    #for word in (bitarr[_:_ + 8] for _ in range(0, len(bitarr), 8)):
        #x = 0
        #for i in range(8):
            #x |= int(word[i] == '1') << i
        #res.append(x)
    #return res

            
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
            
def encoding_arr(res):
    ham = []
    for x in res:
        ham.append(encoding_word(x))
    return ham

def bug_gen(data):
    bug_data = []
    cnt = [0,0,0]
    for x in data:
        ty = random.randint(0, 2)
        cnt[ty] += 1
        if ty == 0:
            bug_data.append(x)
        elif ty == 1:
            bug_data.append(x ^ (1 << random.randint(0, word_len + 14)))
        else:
            i = random.randint(0, word_len + 14)
            j = random.randint(0, word_len + 14)
            while j == i:
                j = random.randint(0, word_len + 14)
            x ^= 1 << i
            x ^= 1 << j
            bug_data.append(x)
    return bug_data, cnt

def popcount(x):
    if x == 0: 
        return 0
    return (x & 1) + popcount(x >> 1)


def sender(client, data):
    for chunk in (data[_:_+ 10] for _ in range(0, len(data), 10)):
        client.send(len(chunk).to_bytes(2, "big"))
        client.send(chunk)
    client.send(b"\x00\x00")

f = open("text.txt", "r", encoding="utf-8")
text = f.read().encode()
print("encoding start")
bitarr = byte_to_origarr(text)
code = encoding_arr(bitarr)
res, cnt = bug_gen(code)
B = b''
for x in res:
    B += x.to_bytes(10, "big")
print("count words with")
print("0 bugs", cnt[0])
print("1 bugs", cnt[1])
print("2 bugs", cnt[2])

client = socket.socket()
client.connect(('localhost', 9090))   
print("sending start")
sender(client, B)
data = client.recv(1024)
print("result")
print(data.decode())

client.close()
