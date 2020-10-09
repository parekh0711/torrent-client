import bencodepy
from bencodepy import *
from torrentool.api import Torrent
from modules import *
f=open("mulan.torrent","rb")
f = f.read()
# print(f)
# input()
trial = decode(f)
print(trial[b'info'].keys())
# print(trial[b'info'][b'piece length'])
# print(trial[b'info'][b'pieces'])
hash  = trial[b'info'][b'pieces']
print(hash)
print(len(hash))
# print(hash)
# my_torrent = Torrent.from_file('dddd.torrent')
# hashes=my_torrent.info_hash
#
# print(hashes)
