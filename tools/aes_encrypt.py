#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/22 18:13
# -------------------------------
"""
aes加密解密工具 目前仅支持ECB/CBC 块长度均为128位 padding只支持pkcs7/zero_padding(aes中没有pkcs5 能用的pkcs5其实是执行的pkcs7) 后续有需要再加
pycryptdemo限制 同一个aes加密对象不能即加密又解密 所以当加密和解密都需要执行时 需要重新new一个对象增加额外开销
 -- A cipher object is stateful: once you have encrypted a message , you cannot encrypt (or decrypt) another message using the same object.　
"""
try:
    from Crypto.Cipher import AES
except:
    print("检测到还未安装 pycryptdemo 请按照md的方法安装")
    exit(0)
from binascii import b2a_hex, a2b_hex
from base64 import b64encode, b64decode
class AES_Ctypt:
    def __init__(self, key, iv=None, mode="ECB"):
        if len(key) % 16 != 0:
            key = key + (AES.block_size - len(key) % AES.block_size) * chr(0)
        self.key = key.encode("utf-8")
        if mode == "ECB":
            self.mode = AES.MODE_ECB
        elif mode == "CBC":
            self.mode = AES.MODE_CBC
        else:
            print("您选择的加密方式错误")
        if iv is None:
            self.cipher = AES.new(self.key, self.mode)
        else:
            if isinstance(iv, str):
                self.cipher = AES.new(self.key, self.mode, iv.encode("utf-8"))
            else:
                print("偏移量不为字符串")
    def encrypt(self, data, padding="pkcs7", b64=False):
        bs = AES.block_size
        pkcs7_padding = lambda s: s + (bs - len(s.encode()) % bs) * chr(bs - len(s.encode()) % bs)
        zero_padding = lambda s: s + (bs - len(s) % bs) * chr(0)
        pad = pkcs7_padding if padding=="pkcs7" else zero_padding
        data = self.cipher.encrypt(pad(data).encode("utf8"))
        encrypt_data = b64encode(data) if b64 else b2a_hex(data) # 输出hex或者base64
        return encrypt_data.decode('utf8')
    def decrypt(self, data, b64=False):
        data = b64decode(data) if b64 else a2b_hex(data)
        decrypt_data = self.cipher.decrypt(data).decode()
        # 去掉padding
        # pkcs7_unpadding = lambda s: s.replace(s[-1], "")
        # zero_unpadding = lambda s: s.replace(chr(0), "")
        # unpadding = pkcs7_unpadding if padding=="pkcs7" else zero_unpadding
        unpadding = lambda s: s.replace(s[-1], "")
        return unpadding(decrypt_data)