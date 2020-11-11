def initialise_variables(torrent_file_name):
    modules.multi_torrent_flag = False
    modules.temp_name=''
    torr = open(torrent_file_name,'rb')
    _dic = decode(torr.read())
    modules.hash_string = _dic[b'info'][b'pieces']
    modules.file_name = _dic[b'info'][b'name'].decode()
    modules.total_size=0
    if b'files' in _dic[b'info'].keys():
        modules.multi_torrent_flag = True
        modules.temp_name='TEMP'
        ls=_dic[b'info'][b'files']
        # input(ls)
        files_details=[]
        for e in ls:
            modules.total_size+=e[b'length']
            files_details.append((e[b'path'][0].decode(),e[b'length']))
        modules.files_details=files_details
        # input(modules.files_details)
    else:
        modules.total_size = _dic[b'info'][b'length']

    modules.total_pieces = len(modules.hash_string)//20
    modules.piece_len = _dic[b'info'][b'piece length']
    tr = encode(_dic[b'info'])
    modules.hashes=[hashlib.sha1(tr).hexdigest()]

    ty=_dic[b'announce-list']
    modules.trackers=[]
    for i in range(len(ty)):
    	a=[]
    	url=ty[i][0].decode()
    	a.append(url)
    	modules.trackers.append(a)

    modules.recieved_data = [0 for _ in range(modules.total_pieces)]
    modules.bitfield = [0 for _ in range(modules.total_pieces)]
    while len(modules.bitfield)%8!=0:
        modules.bitfield.append(0)

    modules.connected_peers=[]
    modules.download_rates = defaultdict(lambda:0)
    modules.end_all_threads = False
    # print(round(modules.total_size%modules.piece_len/16384),modules.total_pieces)
    # input()

import modules
import hashlib
from bencodepy import decode,encode
from collections import defaultdict
import sys
#
# if len(sys.argv)<2:
#     print("Error.")
#     print("Run as python3 <path to torrent file>")
#     sys.exit(0)

initialise_variables("../trial.torrent")


from udp import *
from peer import *
from _thread import start_new_thread
from bitfield import *
from piece import *
import sys
# my_torrent = Torrent.from_file('../trial2.torrent')
# trackers = my_torrent.announce_urls
# input(trackers)
# hashes=[my_torrent.info_hash]

def active_peer(clientsocket,peer_bitfield,ip_address):
    buffer = create_interested_message()
    print("sending interested")
    clientsocket.send(buffer)
    clientsocket.settimeout(2)
    while True:
        try:
            message = clientsocket.recv(2048)
            if message:
                break
            else:
                continue
        except Exception as e:
            print("failed",e)
            if ip_address in connected_peers:
                connected_peers.remove(ip_address)
            return
    print("parsing peer")
    resp = parse_peer_response(message)
    print(resp)
    if resp:
        print(ip,port)
        req = create_have_request(clientsocket,peer_bitfield,ip_address)
        print("done with req")
    else:
        if ip_address in connected_peers:
            connected_peers.remove(ip_address)
        return
    if ip_address in connected_peers:
        connected_peers.remove(ip_address)
    return

threads=[]

while 0 in recieved_data:
    print("hi")
    for tracker in trackers:
        tracker = urlparse(tracker[0])
        if 0 not in recieved_data:
            break
        try:
            if tracker.scheme == 'udp':
                # print('connecting to: ', tracker.hostname)
                # connection = (socket.gethostbyname(tracker.hostname), tracker.port)
                # request, transaction_id = udp_create_connection_request()
                # sock.sendto(request, connection)
                # buffer = sock.recvfrom(1048)[0]
                # connection_id = udp_parse_connection_response(buffer, transaction_id)
                # # print("conn id",connection_id)
                #
                # req,transaction_id = create_udp_announce_request(connection_id,hashes)
                # # print("req=",req)
                # sock.sendto(req,connection)
                # buf = sock.recvfrom(1048)[0]
                # try:
                #     ret,peers=udp_parse_announce_response(buf, transaction_id)
                # except:
                #     continue
                #
                handshake,peer_id=create_handshake_message(hashes)
                print(handshake)
                print("Now trying")
                peers = [{'IP':"210.212.183.7","port":6885}]
                for index in range(len(peers)):
                    ip=peers[index]['IP']
                    port=peers[index]['port']
                    print(ip,port)
                    if ip in connected_peers:
                        continue
                    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    clientsocket.settimeout(1)
                    print("trying")
                    try:
                        clientsocket.connect((ip,port))
                    except:
                        print("nahi hua")
                        continue
                    print('connected')
                    clientsocket.send(handshake)
                    print("Okay....")
                    messages=[]
                    while True:
                        clientsocket.settimeout(1)
                        try:
                            print("waiting")
                            message = clientsocket.recv(4096)
                            print("Recv",message)
                        except:
                            if messages!=[]:
                                break
                        if not message:
                            break
                        else:
                            messages.append(message)
                    if messages==[]:
                        continue
                    # [print(message) for message in messages]
                    # print("messages =",messages)
                    print("hola")
                    if len(messages)>=1:
                        flag,peer_bitfield = parse_bitfield(messages)
                        print(flag)
                    if not flag or not peer_bitfield: #at this point, we have bitfield
                        print(flag,bitfield)
                        input("CONT")
                        continue
                    input("I am here")
                    # t = Thread(target=active_peer,args=(clientsocket, peer_bitfield,))
                    # threads.append(t)
                    active_peer(clientsocket,peer_bitfield,ip)
                    input("done")
                    # t.start()
                    connected_peers.append(ip)
            elif tracker.scheme == 'http':
                pass
        except socket.gaierror:
            print('Connection to: {err} failed..'.format(err=tracker.hostname))
        except socket.timeout:
            pass

sys.exit(0)
