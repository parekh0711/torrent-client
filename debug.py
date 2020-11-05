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

def active_peer(clientsocket,peer_bitfield):
    buffer = create_interested_message()
    print("sending interested")
    clientsocket.send(buffer)
    clientsocket.settimeout(2)
    try:
        message = clientsocket.recv(2048)
    except Exception as e:
        print("failed",e)
        return
    print("parsing peer")
    resp = parse_peer_response(message)
    if resp:
        print(ip,port)
        req = create_have_request(clientsocket,peer_bitfield)
        print("done with req")
    else:
        return

threads=[]

while 0 in recieved_data:
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
                peers = [{'IP':"127.0.0.1","port":6883}]
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
                            message = clientsocket.recv(4096)
                        except:
                            input("hi1")
                            break
                        if not message:
                            input("hi2")
                            break
                        else:
                            messages.append(message)
                    if messages==[]:
                        input("hi3")
                        continue
                    # [print(message) for message in messages]
                    # print("messages =",messages)
                    print("hola")
                    if len(messages)>=1:
                        flag,peer_bitfield = parse_bitfield(messages)
                        print(flag)
                    if not flag or not peer_bitfield: #at this point, we have bitfield
                        print(flag,bitfield)
                        continue
                    print("I am here")
                    t = Thread(target=active_peer,args=(clientsocket, peer_bitfield,))
                    threads.append(t)
                    # active_peer(clientsocket,peer_bitfield)
                    t.start()
                    connected_peers.append(ip)
            elif tracker.scheme == 'http':
                pass
        except socket.gaierror:
            print('Connection to: {err} failed..'.format(err=tracker.hostname))
        except socket.timeout:
            pass

sys.exit(0)
