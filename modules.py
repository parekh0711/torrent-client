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
import bencodepy
from threading import Thread,Lock
lock = Lock()

torr = open('../trial.torrent','rb')
_dic = bencodepy.decode(torr.read())
hash_string = _dic[b'info'][b'pieces']
total_size = _dic[b'info'][b'length']
total_pieces = len(hash_string)//20
piece_len = _dic[b'info'][b'piece length']
recieved_data = [0 for _ in range(total_pieces)]
bitfield = [0 for _ in range(total_pieces)]
while len(bitfield)%8!=0:
    bitfield.append(0)
