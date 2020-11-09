from bencodepy import decode,encode
resp = b'd5:peers6:%(\xe0\x1b\x1a\xe98:completei1e10:incompletei0e8:intervali1800e12:min intervali1800ee'
_dic = decode(resp)
print(_dic.keys())
print(_dic[b'peers'])

print([1,1,1,0].count(1))
