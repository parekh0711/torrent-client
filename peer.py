from modules import *
import random

def create_handshake_message(hashes):
    pstrlen = 0x13 # default pstrlen for version 1.0
    pstr="BitTorrent protocol"
    reserved=0x0000000000000000
    buffer = bytes.fromhex("13")
    buffer += pack("!19s", str.encode("BitTorrent protocol"))
    buffer += pack("!q", reserved)  # next 8 bytes is reserved
    hex_repr = binascii.a2b_hex(hashes[0])
    buffer += pack("!20s", hex_repr)
    peer_id = '-MY'
    for _ in range(4):
        peer_id+=str(random.randint(0,9))
    peer_id+='-'
    for _ in range(12):
        peer_id+=str(random.randint(0,9))
    buffer += peer_id.encode()
    # print("buffer=",buffer)
    return buffer,peer_id

def create_interested_message():
    length=1
    message_id=2
    buffer = pack(">IB", length, message_id)
    return buffer

def create_choke_message():
    length=1
    message_id=0
    buffer = pack(">IB", length, message_id)
    return buffer

def create_unchoke_message():
    length=1
    message_id=1
    buffer = pack(">IB", length, message_id)
    return buffer

def parse_peer_response(message):
    if not message:
        # print(message)
        # print("Nothing recieved")
        return False
    # print(message)
    # print(message[3])
    # print(message[4])
    if message[4]==1 and message[3]==1:
        # print("unchoked")
        return True
    # print("Not unchoked, recieved",message)
    return False




# def create_bitfield_message():
#     return pack(">IB{}s".format(self.bitfield_length),
#                     self.payload_length,
#                     self.message_id,
#                     self.bitfield_as_bytes)
