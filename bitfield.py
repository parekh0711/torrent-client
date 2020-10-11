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
            #This case is when the second message is the bitfield only.
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
            if len(buf)==length-1:   #if length is send with req 1 and bitfield only in req 2
                bitfield = buf.hex()
                pieces= bin(int(bitfield, base=16))[2:]
                print(pieces)
                print(len(pieces))
                return True,pieces
            else:
                buf=bufs[0][68:]
                buf+=bufs[1]
                print(buf)
                length=buf[3]
                bitfield = buf[5:length+4].hex()
                pieces= bin(int(bitfield, base=16))[2:]
                print(pieces)
                print(len(pieces))
                try:
                    buf = buf[length+4:]
                except:
                    return True,pieces
                print(buf)
                parse_have(buf,pieces)
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

def parse_have(buf,pieces):
    while True:
        try:
            have=buf[0:9]
            length = unpack_from("!i", have)[0]
            if length==5 and have[4]==4:
                have=have[5:]
                print(have)
                piece=unpack_from("!i", have)[0]
                # print(piece)
                # print(pieces[piece])
                pieces=pieces[0:piece]+'1'+pieces[piece+1:]
                # print(pieces[piece])
            buf=buf[9:]
        except:
            # input('return ho gaya')
            return pieces
