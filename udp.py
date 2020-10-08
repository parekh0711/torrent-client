from modules import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

def udp_parse_connection_response(buf, sent_transaction_id):

    print('connecting')
    if len(buf) < 16:
        raise RuntimeError("Wrong response length getting connection id: %s" % len(buf))
    action = unpack_from("!i", buf)[0]  # first 4 bytes is action

    res_transaction_id = unpack_from("!i", buf, 4)[0]  # next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in connection response! Expected %s, got %s"
                       % (sent_transaction_id, res_transaction_id))
    if action == 0x0:
        connection_id = unpack_from("!q", buf, 8)[0]  # unpack 8 bytes from byte 8, should be the connection_id
        print("succesfully connected")
        return connection_id
    elif action == 0x3:
        error = unpack_from("!s", buf, 8)
        raise RuntimeError("Error while trying to get a connection response: %s" % error)

def udp_get_transaction_id():
    return int(random.randrange(0, 255))

def udp_create_connection_request():
    connection_id = 0x41727101980  # default connection id
    action = 0x0  # action (0 = give me a new connection id)
    transaction_id = int(random.randrange(0, 255))
    print("Transaction ID :", transaction_id)
    buffer = pack("!q", connection_id)  # first 8 bytes is connection id
    buffer += pack("!i", action)  # next 4 bytes is action
    buffer += pack("!i", transaction_id)  # next 4 bytes is transaction id

    return buffer, transaction_id

def create_udp_announce_request(connection_id, hashes):
    action= 0x1 #to announce
    print("connect",connection_id)
    transaction_id= udp_get_transaction_id()
    buf = pack("!q", connection_id)
    buf += pack("!i", action)
    buf += pack("!i", transaction_id)
    for hash in hashes:
        hex_repr = binascii.a2b_hex(hash)
        buf += pack("!20s", hex_repr)
    peer_id = '-MY0001-123456654321'.encode()
    buf += peer_id #peer id
    down = 0x00
    up = 0x00
    left = 0x00
    buf += pack("!q", down)
    buf += pack("!q", left)
    buf += pack("!q", up)
    buf += pack("!i", 0x2)                                           #event 2 denotes start of downloading
    buf += pack("!i", 0x0)                                           #IP address set to 0. Response received to the sender of this packet
    key = udp_get_transaction_id()                                          #Unique key randomized by client
    buf += pack("!i", key)
    buf += pack("!i", -1)                                            #Number of peers required. Set to -1 for default
    buf += pack("!i", sock.getsockname()[1])                   #port on which response will be sent
    print("buffff=",buf)
    return (buf, transaction_id)

def udp_parse_announce_response(buf, sent_transaction_id):

    if len(buf) < 20:
        raise RuntimeError("Wrong response length while announcing: %s" % len(buf))
    action = unpack_from("!i", buf)[0] #first 4 bytes is action
    res_transaction_id = unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        print(sent_transaction_id,res_transaction_id)
        raise RuntimeError("Transaction ID doesnt match in announce response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))
    if action == 0x1:
        print("Action is 3")
        ret = dict()
        offset = 8; #next 4 bytes after action is transaction_id, so data doesnt start till byte 8
        ret['interval'] = unpack_from("!i", buf, offset)[0]
        print ("Interval:"+str(ret['interval']))
        offset += 4
        ret['leeches'] = unpack_from("!i", buf, offset)[0]
        print("Leeches:"+str(ret['leeches']))
        offset += 4
        ret['seeds'] = unpack_from("!i", buf, offset)[0]
        print("Seeds:"+str(ret['seeds']))
        offset += 4
        peers = list()
        x = 0
        while offset < len(buf)-4:
            peers.append(dict())
            peers[x]['IP'] = unpack_from("!i",buf,offset)[0]
            peers[x]['IP'] = socket.inet_ntoa(pack("!i",peers[x]['IP']))
            #print("IP: "+socket.inet_ntoa(pack("!i",peers[x]['IP'])))
            # print("IP: "+(peers[x]['IP']))
            offset += 4
            if offset >= len(buf):
                raise RuntimeError("Error while reading peer port")
            peers[x]['port'] = unpack_from("!H",buf,offset)[0]
            # print("Port: "+str(peers[x]['port']))
            offset += 2
            x += 1
        return ret,peers
    else:
        #an error occured, try and extract the error string
        error = unpack_from("!s", buf, 8)
        print("Action="+str(action))
        raise RuntimeError("Error while annoucing: %s" % error)
