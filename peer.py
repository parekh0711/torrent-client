from modules import *

def create_handshake_message(hashes):
    pstrlen = 0x13 # default pstrlen for version 1.0
    pstr="BitTorrent protocol"
    reserved=0x0000000000000000
    buffer = bytes.fromhex("13")
    buffer += pack("!19s", str.encode("BitTorrent protocol"))
    buffer += pack("!q", reserved)  # next 8 bytes is reserved
    for hash in hashes:
        hex_repr = binascii.a2b_hex(hash)
        buffer += pack("!20s", hex_repr)
    peer_id = '-MY0001-123456654321'.encode()
    buffer += peer_id
    print("buffer=",buffer)
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


# def create_bitfield_message():
#     return pack(">IB{}s".format(self.bitfield_length),
#                     self.payload_length,
#                     self.message_id,
#                     self.bitfield_as_bytes)
