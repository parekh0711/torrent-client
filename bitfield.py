from modules import *


def parse_bitfield(bufs):
    global bitfield
    if len(bufs)==1:
        buf = bufs[0][68:]
        length = unpack_from("!i", buf)[0]
        if length == len(buf)-4 and buf[4]==5:
            bf = buf[5:].hex()
            pieces = bin(int(bf, base=16))[2:]
            peer_list = modify(pieces)
            return True, peer_list
        else:
            # print("false")
            return False,None
    elif len(bufs)==2:
        buf = bufs[1]
        length = unpack_from("!i", buf)[0]
        if length == len(buf)-4 and buf[4]==5:
            #This case is when the second message is the bitfield only.
            bf = buf[5:].hex()
            pieces= bin(int(bf, base=16))[2:]
            peer_list = modify(pieces)
            return True,peer_list
        else:
            buf = bufs[0]
            buf = bufs[0][68:]
            if buf[4]==5:
                length=buf[3]
            buf = bufs[1]
            if len(buf)==length-1:   #if length is send with req 1 and bitfield only in req 2
                bf = buf.hex()
                pieces= bin(int(bf, base=16))[2:]
                peer_list = modify(pieces)
                return True, peer_list
            else:
                buf=bufs[0][68:]
                buf+=bufs[1]
                length=buf[3]
                bf = buf[5:length+4].hex()
                pieces= bin(int(bf, base=16))[2:]
                try:
                    buf = buf[length+4:]
                except:
                    peer_list = modify(pieces)
                    return True, peer_list
                parse_have(buf,pieces)
                peer_list = modify(pieces)
                return True, peer_list
            return False,None
    elif len(bufs)==3:
        if bufs[2]==b'\x00\x00\x00\x01\x01':
            buf = bufs[1]
            length = unpack_from("!i", buf)[0]
            if length == len(buf)-4 and buf[4]==5:
                bf = buf[5:].hex()
                pieces= bin(int(bf, base=16))[2:]
                peer_list = modify(pieces)
                return True, peer_list
            else:
                # print("false")
                return False,None
    return False,None

def modify(p):
    global bitfield
    p = list(map(int,list(p)))
    if len(p)!=len(bitfield):
        return None
    with lock:
        for index in range(len(bitfield)):
            bitfield[index]+=p[index]
    return p

def parse_have(buf,pieces):
    while True:
        try:
            have=buf[0:9]
            length = unpack_from("!i", have)[0]
            if length==5 and have[4]==4:
                have=have[5:]
                piece=unpack_from("!i", have)[0]
                pieces=pieces[0:piece]+'1'+pieces[piece+1:]
            buf=buf[9:]
        except:
            return pieces
