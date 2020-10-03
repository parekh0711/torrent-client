from torrentool.api import Torrent
import random
import socket
import struct
import binascii
from urllib import parse
from urllib.parse import urlparse

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
# Reading and modifying an existing file.
my_torrent = Torrent.from_file('trial.torrent')
trackers = my_torrent.announce_urls
hashes=[my_torrent.info_hash]

def udp_parse_connection_response(buf, sent_transaction_id):

    print('connecting')
    if len(buf) < 16:
        raise RuntimeError("Wrong response length getting connection id: %s" % len(buf))
    action = struct.unpack_from("!i", buf)[0]  # first 4 bytes is action

    res_transaction_id = struct.unpack_from("!i", buf, 4)[0]  # next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in connection response! Expected %s, got %s"
                       % (sent_transaction_id, res_transaction_id))
    if action == 0x0:
        connection_id = struct.unpack_from("!q", buf, 8)[0]  # unpack 8 bytes from byte 8, should be the connection_id
        print("succesfully connected")
        return connection_id
    elif action == 0x3:
        error = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error while trying to get a connection response: %s" % error)

def udp_get_transaction_id():
    return int(random.randrange(0, 255))

def udp_create_connection_request():
    connection_id = 0x41727101980  # default connection id
    action = 0x0  # action (0 = give me a new connection id)
    transaction_id = int(random.randrange(0, 255))
    print("Transaction ID :", transaction_id)
    buffer = struct.pack("!q", connection_id)  # first 8 bytes is connection id
    buffer += struct.pack("!i", action)  # next 4 bytes is action
    buffer += struct.pack("!i", transaction_id)  # next 4 bytes is transaction id

    return buffer, transaction_id

def udp_parse_scrape_response(buf, sent_transaction_id, hashes):

    if len(buf) < 16:
        raise RuntimeError("Wrong response length while scraping: %s" % len(buf))
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action
    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in scrape response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))
    if action == 0x2:
        ret = {}
        offset = 8; #next 4 bytes after action is transaction_id, so data doesnt start till byte 8
        for hash in hashes:
            seeds = struct.unpack_from("!i", buf, offset)[0]
            offset += 4
            complete = struct.unpack_from("!i", buf, offset)[0]
            offset += 4
            leeches = struct.unpack_from("!i", buf, offset)[0]
            offset += 4
            ret[hash] = { "seeds" : seeds, "peers" : leeches, "complete" : complete }
        return ret
    elif action == 0x3:
        #an error occured, try and extract the error string
        error = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error while scraping: %s" % error)


def udp_create_scrape_request(connection_id, hashes):
    action = 0x2 #action (2 = scrape)
    print("scrap con= ",connection_id)
    transaction_id = udp_get_transaction_id()
    buf = struct.pack("!q", connection_id) #first 8 bytes is connection id
    buf += struct.pack("!i", action) #next 4 bytes is action
    buf += struct.pack("!i", transaction_id) #followed by 4 byte transaction id
    #from here on, there is a list of info_hashes. They are packed as char[]
    for hash in hashes:
        # print("hash=",hash,type(hash))
        hex_repr = binascii.a2b_hex(hash)
        # print("hi:",hex_repr,type(hex_repr))
        buf += struct.pack("!20s", hex_repr)
    return (buf, transaction_id)

def create_udp_announce_request(connection_id, hashes):
    action= 0x1 #to announce
    print("connect",connection_id)
    transaction_id= udp_get_transaction_id()
    buf = struct.pack("!q", connection_id)
    buf += struct.pack("!i", action)
    buf += struct.pack("!i", transaction_id)
    for hash in hashes:
        hex_repr = binascii.a2b_hex(hash)
        buf += struct.pack("!20s", hex_repr)
    peer_id = '084fff3d4a32c5679859af4b9e8dbb7f60716347'
    buf += struct.pack("!20s", binascii.a2b_hex(peer_id)) #peer id
    down = 0x00
    up = 0x00
    left = 0x00
    buf += struct.pack("!q", down)
    buf += struct.pack("!q", left)
    buf += struct.pack("!q", up)
    buf += struct.pack("!i", 0x2)                                           #event 2 denotes start of downloading
    buf += struct.pack("!i", 0x0)                                           #IP address set to 0. Response received to the sender of this packet
    key = udp_get_transaction_id()                                          #Unique key randomized by client
    buf += struct.pack("!i", key)
    buf += struct.pack("!i", -1)                                            #Number of peers required. Set to -1 for default
    buf += struct.pack("!i", sock.getsockname()[1])                   #port on which response will be sent
    print("buffff=",buf)
    return (buf, transaction_id)


def udp_parse_announce_response(buf, sent_transaction_id):
    #print "Response is:"+str(buf)
    print("resp=",buf)
    if len(buf) < 20:
        raise RuntimeError("Wrong response length while announcing: %s" % len(buf))
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action
    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        print(sent_transaction_id,res_transaction_id)
        raise RuntimeError("Transaction ID doesnt match in announce response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))
    print("Reading Response")
# 0           32-bit integer  action          1 // announce
# 4           32-bit integer  transaction_id
# 8           32-bit integer  interval
# 12          32-bit integer  leechers
# 16          32-bit integer  seeders
# 20 + 6 * n  32-bit integer  IP address
# 24 + 6 * n  16-bit integer  TCP port
# 20 + 6 * N
    if action == 0x1:
        print("Action is 3")
        ret = dict()
        offset = 8; #next 4 bytes after action is transaction_id, so data doesnt start till byte 8
        ret['interval'] = struct.unpack_from("!i", buf, offset)[0]
        print ("Interval:"+str(ret['interval']))
        offset += 4
        ret['leeches'] = struct.unpack_from("!i", buf, offset)[0]
        print("Leeches:"+str(ret['leeches']))
        offset += 4
        ret['seeds'] = struct.unpack_from("!i", buf, offset)[0]
        print("Seeds:"+str(ret['seeds']))
        offset += 4
        peers = list()
        x = 0
        while offset < len(buf)-4:
            peers.append(dict())
            peers[x]['IP'] = struct.unpack_from("!i",buf,offset)[0]
            print("IP: "+socket.inet_ntoa(struct.pack("!i",peers[x]['IP'])))
            offset += 4
            if offset >= len(buf):
                raise RuntimeError("Error while reading peer port")
            peers[x]['port'] = struct.unpack_from("!H",buf,offset)[0]
            print("Port: "+str(peers[x]['port']))
            offset += 2
            x += 1
        return ret,peers
    else:
        #an error occured, try and extract the error string
        error = struct.unpack_from("!s", buf, 8)
        print("Action="+str(action))
        raise RuntimeError("Error while annoucing: %s" % error)


for tracker in trackers[:30]:
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
            #
            # req, transaction_id = udp_create_scrape_request(connection_id, hashes)
            # sock.sendto(req, connection)
            # buf = sock.recvfrom(2048)[0]
            # print(udp_parse_scrape_response(buf, transaction_id, hashes))

            req,transaction_id = create_udp_announce_request(connection_id,hashes)
            print("req=",req)
            sock.sendto(req,connection)
            buf = sock.recvfrom(1048)[0]
            print(udp_parse_announce_response(buf, transaction_id))


        elif tracker.scheme == 'http':
            pass  # do nothing for now

    except socket.gaierror:
        print('Connection to: {err} failed..'.format(err=tracker.hostname))
    except socket.timeout:
        pass
