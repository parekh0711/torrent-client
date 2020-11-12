from modules import *
from peer import *
from _thread import start_new_thread
from bitfield import *
import socket,sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


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

def maintain_upload():
	global current_download_speed,global_sleep_upload
	time_passed=0
	while 0 in recieved_data:
		sleep(1)
		time_passed+=1
		uploaded_pieces = sum(upload_rates.values())
		current_upload_speed=(uploaded_pieces*piece_len)/time_passed
		if allowed_upload>current_upload_speed:
			if global_sleep_upload>0:
				with lock:
					global_sleep_upload-=1
			continue
		else:
			with lock:
				global_sleep_upload+=1
	return

def choke_unchoke_mechanism():
	count = 0
	while True:
		for peer in choked:
			if download_rates[peer]>0:
				sorted_unchoked = sorted(unchoked,key=lambda x:download_rates[x])
				#comparing the slowest peer that is unchoked with our choked peer
				if download_rates[peer]>download_rates[sorted_unchoked[0]]:
					with lock:
						unchoked.append(peer)
						choked.append(sorted_unchoked[0])
						try:
							unchoked.remove(sorted_unchoked[0])
						except:
							pass
		sleep(10)
		count+=1
		if count%3==0:
			#every 30 seconds, optimistically unchoking one peer
			if choked!=[]:
				with lock:
					unchoked.append(choked.pop(0))
					choked.append(unchoked.pop(0))
		if end_all_threads == True:
			return

def create_handshake_bitfield():
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
	try:
		length=unpack_from("!i",req)[0]
		id=unpack_from("!b",req,4)[0]
		if id==6:
			index=unpack_from("!i",req,5)[0]
			begin=unpack_from("!i",req,9)[0]
			req_length=unpack_from("!i",req,13)[0]
			spec=[index,begin,req_length]
			# print("spec is",spec)
			return spec
		elif id==2:
			return [True]
		else:
			return []
	except:
		return []

def check_if_piece(index):
	if recieved_data[index]==1:
		return True
	else:
		return False

def create_piece_request(data,index,block):
	length = len(data)+13
	id = 7
	buffer = pack("!i",length)
	buffer += pack("!b",id)
	buffer += pack("!i",index)
	buffer += pack("!i",block)
	buffer +=data
	# print(length,len(buffer))
	return buffer


#thread for seeding activities
def peer_thread(conn,addr):
	global peers
	print("Started")
	mess=conn.recv(4096)
	print(mess)
	response = handshake_parse(mess,conn)
	if response[0]==False:
		print("returning")
		with lock:
			if addr in peers:
				peers.remove(addr)
		return
	# print("cont")
	buffer = create_handshake_bitfield()
	conn.send(buffer[0])
	conn.send(buffer[1])
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
		with lock:
			if addr in peers:
				peers.remove(addr)
		return
	while True:
		if parse_interested(interested)==True and addr in unchoked:
			try:
				conn.send(create_unchoke_message())
				break
			except:
				with lock:
					if addr in peers:
						peers.remove(addr)
				return
		else:
			#top 4 algo has not allowed us to unchoke him yet
			try:
				conn.send(create_choke_message())
			except:
				with lock:
					if addr in peers:
						peers.remove(addr)
				return
			# we will wait for 30 seconds and see if he has been unchoked
			while True:
				sleep(30)
				if addr in peers:
					if addr in unchoked:
						break
					else:
						continue
				else:
					with lock:
						if addr in peers:
							peers.remove(addr)
					return

	while True:
		# in between sending pieces, this peer got choked, so we will send choke
		if addr in choked:
			try:
				conn.send(create_choke_message())
			except:
				with lock:
					if addr in peers:
						peers.remove(addr)
				return
			while True:
				sleep(30)
				if addr in peers:
					if addr in unchoked:
						break
					else:
						continue
				else:
					with lock:
						if addr in peers:
							peers.remove(addr)
					return
			#wait till 30 seconds and if unchoked, send unchoke and continue
			try:
				conn.send(create_unchoke_message())
			except:
				with lock:
					if addr in peers:
						peers.remove(addr)
				return
		req=conn.recv(4098)
		try:
			spec=parse_request(req)
			# print(spec)
		except socket.timeout:
			continue
		except:
			print("go")
			with lock:
				if addr in peers:
					peers.remove(addr)
			return
		if spec==[]:
			with lock:
				if addr in peers:
					peers.remove(addr)
			return
		elif spec==[True]:
			continue
		print("here")
		index=spec[0]#since it returns list
		if check_if_piece(index)==True or True:
			sleep(global_sleep_upload)
			if spec[2]<=16384 and spec[2]<=piece_len:#spec[2] has the requested len
				# print("entered with ",index,spec[1])
				with lock:
					file = open(output_path+temp_name+file_name,"r+b")
					file.seek((index * piece_len)+spec[1])
					data=file.read(spec[2])
					file.close()
				buffer = create_piece_request(data,index,spec[1])
				conn.send(buffer)
				with lock:
					upload_rates[conn]+=1
			else:
				continue
	with lock:
		if addr in peers:
			peers.remove(addr)
	return

# create_bitfield()
peers=[]
choked=[]
unchoked=[]
seed_ip = ''
seed_port = 6882

def seeder_main():
	server.bind((seed_ip, seed_port))
	server.listen(100)
	# print("listening for connections")
	start_new_thread(choke_unchoke_mechanism,())
	start_new_thread(maintain_upload,())
	while True:
		conn, addr = server.accept()
		print("accepted")
		with lock:
			peers.append(addr)
		if len(peers)<4:
			unchoked.append(addr)
		else:
			choked.append(addr)
		start_new_thread(peer_thread,(conn,addr))

	server.close()
