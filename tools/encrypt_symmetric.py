#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/10/24 22:09
# -------------------------------
# !/usr/bin/python3
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
    from Crypto.Cipher import AES, DES, DES3
except:
    print("检测到还未安装 pycryptdemo 请按照md的方法安装")
    exit(0)
from binascii import b2a_hex, a2b_hex
from base64 import b64encode, b64decode


class Crypt:
    def __init__(self, crypt_type: str, key, iv=None, mode="ECB"):
        """

        :param crypt_type: 对称加密类型 支持AES, DES, DES3
        :param key: 密钥 (aes可选 16/32(24位暂不支持 以后遇到有需要再补)  des 固定为8 des3 24(暂不支持16 16应该也不会再使用了) 一般都为24 分为8长度的三组 进行三次des加密
        :param iv: 偏移量
        :param mode: 模式 CBC/ECB
        """
        if crypt_type.upper() not in ["AES", "DES", "DES3"]:
            raise Exception("加密类型错误, 请重新选择 AES/DES/DES3")
        self.crypt_type = AES if crypt_type.upper() == "AES" else DES if crypt_type.upper() == "DES" else DES3
        self.block_size = self.crypt_type.block_size
        if self.crypt_type == DES:
            self.key_size = self.crypt_type.key_size
        elif self.crypt_type == DES3:
            self.key_size = self.crypt_type.key_size[1]
        else:
            if len(key) <= 16:
                self.key_size = self.crypt_type.key_size[0]
            elif len(key) > 24:
                self.key_size = self.crypt_type.key_size[2]
            else:
                self.key_size = self.crypt_type.key_size[1]
                print("当前aes密钥的长度只填充到24 若需要32 请手动用 chr(0) 填充")
        if len(key) > self.key_size:
            key = key[:self.key_size]
        else:
            if len(key) % self.key_size != 0:
                key = key + (self.key_size - len(key) % self.key_size) * chr(0)
        self.key = key.encode("utf-8")
        if mode == "ECB":
            self.mode = self.crypt_type.MODE_ECB
        elif mode == "CBC":
            self.mode = self.crypt_type.MODE_CBC
        else:
            raise Exception("您选择的加密模式错误")
        if iv is None:
            self.cipher = self.crypt_type.new(self.key, self.mode)
        else:
            if isinstance(iv, str):
                iv = iv[:self.block_size]
                self.cipher = self.crypt_type.new(self.key, self.mode, iv.encode("utf-8"))
            elif isinstance(iv, bytes):
                iv = iv[:self.block_size]
                self.cipher = self.crypt_type.new(self.key, self.mode, iv)
            else:
                raise Exception("偏移量不为字符串")

    def encrypt(self, data, padding="pkcs7", b64=False):
        """

        :param data: 目前暂不支持bytes 只支持string 有需求再补
        :param padding: pkcs7/pkck5 zero
        :param b64: 若需要得到base64的密文 则为True
        :return:
        """
        pkcs7_padding = lambda s: s + (self.block_size - len(s.encode()) % self.block_size) * chr(
            self.block_size - len(s.encode()) % self.block_size)
        zero_padding = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(0)
        pad = pkcs7_padding if padding == "pkcs7" else zero_padding
        data = self.cipher.encrypt(pad(data).encode("utf8"))
        encrypt_data = b64encode(data) if b64 else b2a_hex(data)  # 输出hex或者base64
        return encrypt_data.decode('utf8')

    def decrypt(self, data, b64=False):
        """
        对称加密的解密
        :param data: 支持bytes base64 hex list 未做填充 密文应该都是数据块的倍数 带有需求再补
        :param b64: 若传入的data为base64格式 则为True
        :return:
        """
        if isinstance(data, list):
            data = bytes(data)
        if not isinstance(data, bytes):
            data = b64decode(data) if b64 else a2b_hex(data)
        decrypt_data = self.cipher.decrypt(data).decode()
        # 去掉padding
        # pkcs7_unpadding = lambda s: s.replace(s[-1], "")
        # zero_unpadding = lambda s: s.replace(chr(0), "")
        # unpadding = pkcs7_unpadding if padding=="pkcs7" else zero_unpadding
        unpadding = lambda s: s.replace(s[-1], "")
        return unpadding(decrypt_data)
