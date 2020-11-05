from modules import *
from udp import *
from peer import *
from _thread import start_new_thread
from bitfield import *
from piece import *
import socket,sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peers=[]
clients=[]
#parsing normal handshake to get infohash and peerid
def handshake_parse(buf,conn):
	if len(buf) < 68:
		print("keeda")
		return [False]
	pstrlen = unpack_from("!i", buf)[0]  # first 4 bytes is action
	pstr = unpack_from("!19s", buf,1)[0]
	if pstr != b"BitTorrent protocol":
		print("something",pstr)
		return [False]
	reserved = unpack_from("!q", buf, 8)[0]
	info_hash = unpack_from("!20s", buf, 28)[0].hex()
	peerid = unpack_from("!20s", buf, 20)[0]
	if info_hash == hashes[0]:
		return [True,peerid]
	else:
		print("failed",info_hash,hashes)
		conn.close()

def create_handshake_bitfield():
	pstrlen = 0x13 # default pstrlen for version 1.0
	pstr="BitTorrent protocol"
	reserved=0x0000000000000000
	buffer = bytes.fromhex("13")
	buffer += pack("!19s", str.encode("BitTorrent protocol"))
	buffer += pack("!q", reserved)  # next 8 bytes is reserved
	for hash in hashes:
		hex_repr = binascii.a2b_hex(hash)
		buffer += pack("!20s", hex_repr)
	peer_id = '-MY0001-123450169321'.encode()
	buffer += peer_id
	b=create_bitfield()
	return buffer,b

def create_bitfield():
	rd=recieved_data.copy()
	for i in range(len(rd)):
		if rd[i]==0:
			rd[i]=1
	while len(rd)%8!=0:
		rd.append(0)
	# print(rd,bitfield)
	# input()
	temp = ''.join(list(map(str,rd)))
	temp = int(temp, 2).to_bytes((len(temp) + 7)//8,'big')
	length=1+len(temp)
	id=5
	buffer=pack("!IB",length,id)
	buffer+=temp
	return buffer

def parse_interested(interested):
	length=unpack_from("!i",interested)[0]
	id=unpack_from("!b",interested,4)[0]
	if id==2:
		return True
	else:
		return False

def parse_request(req):
	length=unpack_from("!i",req)[0]
	id=unpack_from("!b",req,4)[0]
	if id==6:
		index=unpack_from("!i",req,5)[0]
		begin=unpack_from("!i",req,9)[0]
		req_length=unpack_from("!i",req,13)[0]
		spec=[index,begin,req_length]
		input(spec)
		return spec

def check_if_piece(index):
	if recieved_data[index]==1:
		return True
	else:
		return False

#thread for seeding activities
def peer_thread(conn,addr):
	print("Started")
	mess=conn.recv(4096)
	print(mess)
	response = handshake_parse(mess,conn)
	if response[0]==False:
		print("returning")
		return
	print("cont")
	buffer = create_handshake_bitfield()
	conn.send(buffer[0])
	conn.send(buffer[1])
	while True:
		while True:
			try:
				interested=conn.recv(2046)
			except Exception as e:
				print(e)
				continue
			if interested == b'':
				continue
			else:
				break
		if not interested:
			return
		# print(parse_interested(interested))
		if parse_interested(interested)==True:
			conn.send(create_unchoke_message())
			print("sent")
			req=conn.recv(4098)
			spec=parse_request(req)
			index=spec[0]#since it returns list
			if check_if_piece(index)==True or True:
				if spec[2]<=16384 and spec[2]<=piece_len:#spec[2] has the requested len
					file = open(file_name,"r+b")
					file.seek((index * piece_len)+(spec[1]*16384))
					data=file.read(spec[2])
					conn.send(data)
					file.close()
				else:
					pass
					#i was confused

# create_bitfield()
ip = '127.0.0.1'
port = 9005
server.bind((ip, port))
server.listen(100)
print("listening for connections")
while True:
	conn, addr = server.accept()
	print("accepted")
	start_new_thread(peer_thread,(conn,addr))

server.close()
