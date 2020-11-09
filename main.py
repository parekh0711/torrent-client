def initialise_variables():
    modules.multi_torrent_flag = False
    modules.temp_name=''
    torr = open('../z.torrent','rb')
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
        input(modules.files_details)
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
initialise_variables()

from udp import *
from peer import *
from _thread import start_new_thread
from bitfield import *
from piece import *
from seed import seeder_main
from file import split_files
import sys

def active_peer(clientsocket,peer_bitfield,ip_address):
    buffer = create_interested_message()
    # print("sending interested")
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
            # print("failed",e)
            if ip_address in connected_peers:
                connected_peers.remove(ip_address)
            return
    # print("parsing peer")
    resp = parse_peer_response(message)
    if resp:
        # print(ip,port)
        if 0 not in recieved_data:
            return
        req = create_have_request(clientsocket,peer_bitfield,ip_address)
        # print("done with req")
    else:
        if ip_address in connected_peers:
            connected_peers.remove(ip_address)
        return
    if ip_address in connected_peers:
        connected_peers.remove(ip_address)
    return

def update_progress():
    # cnt =
    while True:
        perc = recieved_data.count(1)/len(recieved_data)*100
        print('\r[{0}] {1}%'.format('#'*round(perc), round(perc,2)),end='')
        sleep(1)
        if 0 not in recieved_data:
            perc = 100
            print('\r[{0}] {1}%'.format('#'*100,100,end=''))
            return

threads=[]

k = Thread(target=update_progress,args=())
k.start()
s = Thread(target=seeder_main,args=())
s.daemon=True
s.start()

while 0 in recieved_data:
    for tracker in trackers:
        if 0 not in recieved_data:
            break
        if len(connected_peers)>=allowed_length:
            sleep(5)
            break
        t = tracker[0]
        tracker = urlparse(tracker[0])
        if 0 not in recieved_data:
            break
        try:
            if tracker.scheme == 'udp':
                connection = (socket.gethostbyname(tracker.hostname), tracker.port)
                request, transaction_id = udp_create_connection_request()
                sock.sendto(request, connection)
                buffer = sock.recvfrom(1048)[0]
                try:
                    connection_id = udp_parse_connection_response(buffer, transaction_id)
                except:
                    continue

                req,transaction_id = create_udp_announce_request(connection_id,hashes)
                sock.sendto(req,connection)
                buf = sock.recvfrom(1048)[0]
                try:
                    ret,peers=udp_parse_announce_response(buf, transaction_id)
                except:
                    continue
                handshake,peer_id=create_handshake_message(hashes)
                for index in range(len(peers)):
                    if 0 not in recieved_data:
                        break
                    ip=peers[index]['IP']
                    port=peers[index]['port']
                    # print(ip,port)
                    if ip in connected_peers:
                        continue
                    clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    clientsocket.settimeout(1)
                    # print("trying")
                    try:
                        clientsocket.connect((ip,port))
                    except:
                        # print("nahi hua")
                        continue
                    # print('connected')
                    clientsocket.send(handshake)
                    # print("Okay....")
                    messages=[]
                    while True:
                        clientsocket.settimeout(1)
                        try:
                            message = clientsocket.recv(4096)
                        except:
                            if messages!=[]:
                                break
                        if not message:
                            break
                        else:
                            messages.append(message)
                    if messages==[]:
                        continue
                    if len(messages)>=1:
                        try:
                            flag,peer_bitfield = parse_bitfield(messages)
                        except:
                            continue
                        # print(flag)
                    if not flag or not peer_bitfield: #at this point, we have bitfield
                        # print(flag,bitfield)
                        continue
                    t = Thread(target=active_peer,args=(clientsocket, peer_bitfield,ip,))
                    threads.append(t)
                    # active_peer(clientsocket,peer_bitfield)
                    t.start()
                    connected_peers.append(ip)
            elif tracker.scheme == 'http' or tracker.scheme=='https':
                continue
                params = {
                    "info_hash" : hashes[0],
                    "peer_id" : '-MY0001-123456654321',
                    "port" : '6889',
                    "uploaded" : '0',
                    "downloaded" : '0',
                    "left" : '0'
                }
                # t='http://t.nyaatracker.com/announce'
                print(t+"?"+urlencode(params))
                print(t)
                try:
                    print("hi")
                    response = requests.get(
                        t+"?"+urlencode(params),
                        timeout=2
                    )
                except requests.ConnectionError as e:
                    print("failed")
                    continue
                except:
                    continue
                print("hi")
                if response.status_code < 200 or response.status_code >= 300:
                    print("error",response.status_code)
                    continue
                if b'failure' in response.content or response.content==b'':
                    continue
                print("resp\n",response.content)
                input('wait')
        except socket.gaierror:
            # print('Connection to: {err} failed..'.format(err=tracker.hostname))
            pass
        except socket.timeout:
            pass

if multi_torrent_flag:
    split_files()
print("FILE IS DONE")


sys.exit(0)
