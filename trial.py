from modules import *
print(total_pieces,total_size%32768)
print(len(hash_string)/20)
print(piece_len/2)

print(len(resp))
length = unpack_from("!i",resp)[0]
id = unpack_from("!b",resp,4)[0]
piece = unpack_from("!i",resp,5)[0]
block = unpack_from("!i",resp,9)[0]
print(length,id,piece,block)
data=resp[13:]
print(data[:10])
hash_object = hashlib.sha1(data)
hash_received = hash_object.digest()
print(hash_received)
