from modules import *

with open('The Subtle Art of Not Giving a Fck - A Counterintuitive Approach to Living a Good Life (2016) (Epub) Gooner', 'rb') as fbson:
    fbson.seek(file_pointers[1])
    bytes_chunk = fbson.read(file_pointers[2] - file_pointers[1])
    with open('tmp.bson', 'wb') as output_file:
        output_file.write(bytes_chunk)
