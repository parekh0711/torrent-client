from struct import *

def parse_bitfield(bufs):
    if len(bufs)==1:
        buf = bufs[0][68:]
        length = unpack_from("!i", buf)[0]
        if length == len(buf)-4 and buf[4]==5:
            bitfield = buf[5:].hex()
            pieces= bin(int(bitfield, base=16))[2:]
            print(pieces)
            print(len(pieces))
            return True,pieces
        else:
            print("false")
            return False, None
    elif len(bufs)==2:
        buf = bufs[1]
        length = unpack_from("!i", buf)[0]
        if length == len(buf)-4 and buf[4]==5:
            bitfield = buf[5:].hex()
            pieces= bin(int(bitfield, base=16))[2:]
            print(pieces)
            print(len(pieces))
            return True,pieces
        else:
            buf = bufs[0]
            buf = bufs[0][68:]
            if buf[4]==5:
                length=buf[3]
                print(length)
            buf = bufs[1]
            if len(buf)==length-1:
                bitfield = buf[5:].hex()
                pieces= bin(int(bitfield, base=16))[2:]
                print(pieces)
                print(len(pieces))
                return True,pieces
            return False, None
    elif len(bufs)==3:
        if bufs[2]==b'\x00\x00\x00\x01\x01':
            buf = bufs[1]
            length = unpack_from("!i", buf)[0]
            if length == len(buf)-4 and buf[4]==5:
                bitfield = buf[5:].hex()
                pieces= bin(int(bitfield, base=16))[2:]
                print(pieces)
                print(len(pieces))
                return True,pieces
            else:
                print("false")
                return False, None
    return False,None
