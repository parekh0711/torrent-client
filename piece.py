from modules import *


def find_rarest(peer_bitfield):
    global bitfield, recieved_data, total_size, total_pieces, piece_len
    with lock:
        sorted_indices = sorted(
            range(len(recieved_data)),
            key=lambda k: (
                recieved_data[k],
                bitfield[k],
            ),
        )
        for index in sorted_indices:
            if recieved_data[index] != 1 and peer_bitfield[index] == 1:
                bitfield[index] += 1
                return index, True
    return -1, False


def parse_block_request(resp, off, p_off):
    length = unpack_from("!i", resp)[0]
    id = unpack_from("!b", resp, 4)[0]
    piece = unpack_from("!i", resp, 5)[0]
    block = unpack_from("!i", resp, 9)[0]
    # print(piece,off,id,block,p_off)
    if piece != off or id != 7:
        return b""
    data = resp[13 : length + 4]
    # print("returning data")
    return data


def create_have_request(socket, peer_bitfield, ip_address):
    global bitfield, recieved_data, total_size, total_pieces, piece_len, global_downloaded_pieces
    while 0 in recieved_data:
        # print(download_rates)
        # print("hi")
        index, check = find_rarest(peer_bitfield)
        if end_all_threads == True:
            return
        if not check:
            # We have taken all possible pieces from this peer
            return
        # print("REQUESTING PIECE",index)
        sleep(global_sleep_download)
        if piece_len > 16384 and (
            index != total_pieces - 1 or total_size % piece_len > 16384
        ):
            resp = b""
            if index != total_pieces - 1:
                calculated_length = math.ceil(piece_len / 16384)
            else:
                calculated_length = math.ceil(total_size % piece_len / 16384)
            for piece_index in range(calculated_length):
                buf = pack(">IB", 13, 6)
                buf += pack("!i", index)
                buf += pack("!i", piece_index * 16384)
                if piece_index == calculated_length - 1:
                    if index == total_pieces - 1:
                        lg = (total_size % piece_len) % 16384
                    elif index != total_pieces - 1 and piece_len % 16384 != 0:
                        lg = piece_len % 16384
                    else:
                        lg = 16384
                else:
                    lg = 16384
                buf += pack("!i", lg)
                # print("REQUESTING BLOCK {} IN PIECE {} WITH SIZE {}".format(piece_index,index,lg))
                socket.send(buf)
                res = b""
                socket.settimeout(4)
                while True:
                    try:
                        temp = socket.recv(32768)
                        res += temp
                    except:
                        break
                if res == b"":
                    break
                check = parse_block_request(res, index, piece_index)
                if check != b"":
                    resp += check
                else:
                    res = b""
                    break
            start = pack("!i", piece_len)
            start += pack("!b", 7)
            start += pack("!i", index)
            start += pack("!i", 0)
            resp = start + resp
            if res == b"":
                # print("problem")
                continue
        else:
            buf = pack(">IB", 13, 6)
            buf += pack("!i", index)
            buf += pack("!i", 0)
            if index == total_pieces - 1:
                lg = total_size % piece_len
            else:
                lg = piece_len
            buf += pack("!i", lg)
            bufs = [buf]
            socket.send(buf)
            resp = b""
            socket.settimeout(2)
            while True:
                try:
                    temp = socket.recv(32768)
                    resp += temp
                except:
                    break
        # input(resp)
        check = parse_piece_request(resp, index)
        if check:
            with lock:
                # global_downloaded_pieces+=1
                # print("PIECE",global_downloaded_pieces)
                recieved_data[index] = 1
                bitfield[index] = 9999
                download_rates[ip_address] += 1
        else:
            # print("hash didnt match")
            pass
    return


def parse_piece_request(resp, off):
    global hash_string, file_name
    if len(resp) == 0:
        # print("length is 0")
        return False
    length = unpack_from("!i", resp)[0]
    id = unpack_from("!b", resp, 4)[0]
    piece = unpack_from("!i", resp, 5)[0]
    if piece != off or id != 7:
        # print("keeda",id,piece,off)
        return False
    block = unpack_from("!i", resp, 9)[0]
    data = resp[13:]
    hash_object = hashlib.sha1(data)
    hash_received = hash_object.digest()
    if hash_received != hash_string[off * 20 : (off * 20) + 20]:
        # print(hash_recieved,hash_string[off*20:(off*20)+20])
        return False
    fn = file_name
    writePiece(output_path + temp_name + fn, off, data)
    # print(length,id,piece,block)
    return True


def writePiece(filename, pieceindex, data):
    global bitfield, recieved_data, total_size, total_pieces, piece_len
    if not os.path.exists(filename):
        os.mknod(filename)
    if recieved_data[pieceindex] == 1:
        return
    with lock:
        file = open(filename, "r+b")
        little = pack("<" + "B" * len(data), *data)
        file.seek(pieceindex * piece_len)
        file.write(little)
        file.flush()
        # print("Wrote (%d) bytes of piece (%d) to %s" % (len(data), pieceindex, filename))
        file.close()
