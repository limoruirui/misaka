#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/23 13:05
# -------------------------------
try:
    from Crypto.PublicKey.RSA import importKey, construct
    from Crypto.Cipher import PKCS1_v1_5
except:
    print("检测到还未安装 pycryptodome 请按照md的方法安装")
    exit(0)
from base64 import b64encode


class RSA_Encrypt:
    def __init__(self, key):
        if isinstance(key, str):
            # 若提供的rsa公钥不为pem格式 则先将hex转化为pem格式
            # self.key = bytes.fromhex(key) if "PUBLIC KEY" not in key else key.encode()
            self.key = self.public_key(key) if "PUBLIC KEY" not in key else key.encode()
        else:
            print("提供的公钥格式不正确")

    def public_key(self, rsaExponent, rsaModulus=10001):
        e = int(rsaExponent, 16)
        n = int(rsaModulus, 16)  # snipped for brevity
        pubkey = construct((n, e)).export_key()
        return pubkey

    def encrypt(self, data, b64=False):
        data = data.encode('utf-8')
        length = len(data)
        default_length = 117
        pub_key = importKey(self.key)
        cipher = PKCS1_v1_5.new(pub_key)
        if length < default_length:
            rsa_text = cipher.encrypt(data)
            return b64encode(rsa_text).decode() if b64 else rsa_text.hex()
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > default_length:
                res.append(cipher.encrypt(data[offset:offset + default_length]))
            else:
                res.append(cipher.encrypt(data[offset:]))
            offset += default_length
        byte_data = b''.join(res)
        return b64encode(byte_data).decode() if b64 else byte_data.hex()
