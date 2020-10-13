from modules import *


def create_have_request(socket,bitfield,data):
    torr = open('../trial.torrent','rb')
    _dic = bencodepy.decode(torr.read())
    hash_string = _dic[b'info'][b'pieces']
    total_size = _dic[b'info'][b'length']
    print(total_size)
    total_pieces = len(hash_string)//20
    piece_len = _dic[b'info'][b'piece length']
    t = input(bitfield)
    if t!='y':
        return
    for index,piece in enumerate(data):
        if piece=='0' and bitfield[index]=='1':
            buf = pack(">IB",13,6)
            buf += pack("!i",index)
            buf += pack("!i",0)
            if index==total_pieces-1:
                lg = total_size%piece_len
                input(lg)
            else:
                lg = piece_len
            buf += pack("!i",lg)
            # print(buf)
            socket.send(buf)
            resp=b''
            print("yo")
            socket.settimeout(4)
            while True:
                try:
                    temp =socket.recv(32768)
                    resp+=temp
                except:
                    break
            check = parse_piece_request(resp,index,hash_string,piece_len)
            if check:
                data= data[:index]+'1'+ data[index+1:]
            else:
                print("hash didnt match")
    print("sorry")
    print("data = ",data)

def parse_piece_request(resp,off,hash_string,piece_len):
    length = unpack_from("!i",resp)[0]
    id = unpack_from("!b",resp,4)[0]
    piece = unpack_from("!i",resp,5)[0]
    if piece!=off or id!=7:
        print(length,id,piece)
        return False
    block = unpack_from("!i",resp,9)
    data=resp[13:length+4]
    hash_object = hashlib.sha1(data)
    hash_received = hash_object.digest()
    if hash_received!=hash_string[off*20:(off*20)+20]:
        print(hash_recieved,hash_string[off*20:(off*20)+20])
        return False
    fn = 'Too Much and Never Enough - Mary Trump.epub'
    writePiece(fn,off,data,piece_len)
    print(length,id,piece,block)
    return True

def write(filename,data,offset):
     try:
         f = open(filename,'r+b')
     except IOError:
         f = open(filename,'wb')
     f.seek(offset)
     f.write(data)
     f.close()

def writePiece(filename, pieceindex, data,piece_len):
    if not os.path.exists(filename):
        os.mknod(filename)
    file = open(filename,"r+b")
    little = pack('<'+'B'*len(data), *data)
    file.seek(pieceindex * piece_len)
    file.write(little)
    file.flush()
    print("Wrote (%d) bytes of piece (%d) to %s" % (len(data), pieceindex, filename))
    file.close()



# piece = b'\x00\x00@\t\x07\x00\x00\x00\x00\x00\x00\x00\x00TorrentGalaxy\r\n Putting P2P back on the rails...\r\n \r\n \r\n For all your torrent > Movie - TV - XXX - Software < needs,\r\n or just to say hi to our friendly staff and community,\r\n \r\n Visit us @ ---> https://torrentgalaxy.to <--- \r\n \r\n Trouble accessing https://torrentgalaxy.to ?\r\n For our up to date official proxy site list checkout https://proxygalaxy.pw\r\n \r\n \r\n \r\n follow us on social media\r\n https://twitter.com/tgxsocial\r\n https://www.facebook.com/tgxsocial1\r\n https://www.instagram.com/tgxsocial\r\n \r\n or join our exclusive members group on Facebook\r\n https://www.facebook.com/groups/174735346567877/\r\n \r\n \r\n TorrentGalaxy is now also accessible via Tor @ http://galaxy2gchufcb3z.onion\r\n\x1aE\xdf\xa3\xa3B\x86\x81\x01B\xf7\x81\x01B\xf2\x81\x04B\xf3\x81\x08B\x82\x88matroskaB\x87\x81\x04B\x85\x81\x02\x18S\x80g\x01\x00\x00\x00(e{\x94\x11M\x9bt\xc0M\xbb\x8cS\xab\x84\x15I\xa9fS\xac\x82\x10\x03M\xbb\x8cS\xab\x84\x16T\xaekS\xac\x82\x10\x8bM\xbb\x8eS\xab\x84\x1cS\xbbkS\xac\x84(e({M\xbb\x8eS\xab\x84\x12T\xc3gS\xac\x84(ew\x05\xecO\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# parse_piece_request(piece)
