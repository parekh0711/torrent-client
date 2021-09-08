import random
import socket
import binascii
import logging
from urllib import parse
from urllib.parse import urlparse, urlencode
from struct import *
from select import *
import os
import hashlib
from bencodepy import decode, encode
from threading import Thread, Lock
import requests
from time import sleep
import math

lock = Lock()

multi_torrent_flag = 0
hash_string = 0
file_name = 0
total_size = 0
multi_torrent_flag = 0
total_pieces = 0
piece_len = 0
hashes = 0
trackers = 0
recieved_data = 0
bitfield = 0
connected_peers = 0
download_rates = 0
upload_rates = 0
end_all_threads = 0
allowed_length = 100
allowed_download = 3125000
allowed_upload = 3125000
files_details = 0
temp_name = ""
output_path = ""
global_sleep_download = 0
global_sleep_upload = 0
global_uploaded_pieces = 0
current_download_speed = 0
