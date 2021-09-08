from modules import *


def copypart(src, dest, start, length, bufsize=1024 * 1024):
    with open(src, "rb") as f1:
        f1.seek(start)
        with open(dest, "wb") as f2:
            while length:
                chunk = min(bufsize, length)
                data = f1.read(chunk)
                f2.write(data)
                length -= chunk


def split_files():
    src = output_path + temp_name + file_name
    offset = 0
    for record in files_details:
        dest = output_path + record[0]
        copypart(src, dest, offset, record[1])
        offset += record[1]
    os.remove(src)
