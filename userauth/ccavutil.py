from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from hashlib import md5

from django.utils.encoding import force_bytes

_iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
# for python 3.9 & pycryptodome, this need to be byte
_iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

BS = 16


def _pad(data):
    return data + (BS - len(data) % BS) * chr(BS - len(data) % BS)


def _unpad(data):
    return data[0:-ord(data[-1])]


def encrypt(plain_text, working_key):
    plain_text = _pad(plain_text)
    enc_cipher = AES.new(md5(force_bytes(working_key)).digest(), AES.MODE_CBC, _iv)
    return hexlify(enc_cipher.encrypt(plain_text)).decode('utf-8')


def decrypt(cipher_text, working_key):
    encrypted_text = unhexlify(cipher_text)
    dec_cipher = AES.new(md5(force_bytes(working_key)).digest(), AES.MODE_CBC, _iv)
    return _unpad(dec_cipher.decrypt(encrypted_text).decode('utf-8'))