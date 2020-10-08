#https://github.com/eliasson/pieces/blob/master/pieces/protocol.py
#https://github.com/gallexis/pytorrent


from udp import *
from peer import *
from _thread import start_new_thread

my_torrent = Torrent.from_file('mulan.torrent')
trackers = my_torrent.announce_urls
hashes=[my_torrent.info_hash]

for tracker in trackers[2:30]:
    tracker = urlparse(tracker[0])
    try:
        if tracker.scheme == 'udp':
            print('connecting to: ', tracker.hostname)
            connection = (socket.gethostbyname(tracker.hostname), tracker.port)
            request, transaction_id = udp_create_connection_request()
            sock.sendto(request, connection)
            buffer = sock.recvfrom(1048)[0]
            connection_id = udp_parse_connection_response(buffer, transaction_id)
            print("conn id",connection_id)

            req,transaction_id = create_udp_announce_request(connection_id,hashes)
            print("req=",req)
            sock.sendto(req,connection)
            buf = sock.recvfrom(1048)[0]
            ret,peers=udp_parse_announce_response(buf, transaction_id)

            print("yoyoyo")
            req,peer_id=create_handshake_message(hashes)

            for index in range(len(peers)):
                ip=peers[index]['IP']
                port=peers[index]['port']
                clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientsocket.settimeout(1)
                print("trying")
                try:
                    clientsocket.connect((ip,port))
                except:
                    continue
                print('connected')
                print(req)
                clientsocket.send(req)
                messages=[]
                while True:
                    clientsocket.settimeout(1)
                    try:
                        message = clientsocket.recv(4096)
                    except:
                        break
                    if not message:
                        break
                    else:
                        messages.append(message)
                if messages==[]:
                    continue
                [print(message) for message in messages]
                print("messages =",messages)
                check = input('waiting.....')
                if check =='c':
                    req=create_interested_message()
                    clientsocket.send(req)
                    print("did")
                    try:
                        buffer = clientsocket.recv(1048)
                    except:
                        continue
                    print("I got",buffer)
                    pass
        elif tracker.scheme == 'http':
            pass  # do nothing for now

    except socket.gaierror:
        print('Connection to: {err} failed..'.format(err=tracker.hostname))
    except socket.timeout:
        pass
