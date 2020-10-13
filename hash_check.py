import bencodepy
import hashlib

torr = open('../trial.torrent','rb')
_dic = bencodepy.decode(torr.read())
hash_string = _dic[b'info'][b'piece length']
# print(len(hash_string)//20)
print(hash_string)
print(hash_string[:20])

hash_object = hashlib.sha1(piece)
pbHash = hash_object.digest()
print(pbHash)
