import random
import socket
import binascii
import logging
from urllib import parse
from urllib.parse import urlparse
from torrentool.api import Torrent
from struct import *
from select import *
import os
import hashlib
from bencodepy import decode,encode
from threading import Thread,Lock
lock = Lock()
multi_torrent_flag = False
torr = open('../trial.torrent','rb')


_dic = decode(torr.read())
hash_string = _dic[b'info'][b'pieces']
file_name = _dic[b'info'][b'name'].decode()
total_size=0
if b'files' in _dic[b'info'].keys():
    multi_torrent_flag = True
    ls=_dic[b'info'][b'files']
    for e in ls:
        total_size+=e[b'length']
        # print(e[b'length'],e[b'path'][0].decode())
else:
    total_size = _dic[b'info'][b'length']


total_pieces = len(hash_string)//20
piece_len = _dic[b'info'][b'piece length']
tr = encode(_dic[b'info'])
hashes=[hashlib.sha1(tr).hexdigest()]
# print(hashes)

ty=_dic[b'announce-list']
trackers=[]
for i in range(len(ty)):
	a=[]
	url=ty[i][0].decode()
	a.append(url)
	trackers.append(a)

# print(trackers)
# print(piece_len)
recieved_data = [0 for _ in range(total_pieces)]
bitfield = [0 for _ in range(total_pieces)]
while len(bitfield)%8!=0:
    bitfield.append(0)

# print(total_pieces)
connected_peers=[]
# print(round(65536/16384))
# print(round(total_size%piece_len/16384))
# print(total_size%piece_len)
# print(round(total_size%piece_len/16384))
# print(total_size)
# print()
#507637
