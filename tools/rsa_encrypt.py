#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/8/23 13:05
# -------------------------------
from Crypto.PublicKey.RSA import importKey
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode

class RSA_Encrypt:
    def __init__(self, key):
        if isinstance(key, str):
            # 若提供的rsa公钥不为pem格式 则先将hex转化为pem格式
            self.key = bytes.fromhex(key) if "PUBLIC KEY" not in key else key.encode()
        else:
            print("提供的公钥格式不正确")
    def Encrypt(self, data, b64=False):
        pub_key = importKey(self.key)
        cipher = PKCS1_v1_5.new(pub_key)
        rsa_text = cipher.encrypt(data.encode("utf8"))
        rsa_text = b64encode(rsa_text).decode() if b64 else rsa_text.hex()
        return rsa_text
# print(b64encode(bytes.fromhex("00A828DB9D028A4B9FC017821C119DFFB8537ECEF7F91D4BC06DB06CC8B4E6B2D0A949B66A86782D23AA5AA847312D91BE07DC1430C1A6F6DE01A3D98474FE4511AAB7E4E709045B61F17D0DC4E34FB4BE0FF32A04E442EEE6B326D97E11AE8F23BF09926BF05AAF65DE34BB90DEBDCEE475D0832B79586B4B02DEED2FC3EA10B3".lower())).decode())