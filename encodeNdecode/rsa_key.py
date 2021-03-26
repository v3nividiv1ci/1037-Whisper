import rsa

# 生成公钥和私钥
(pubkey, privkey) = rsa.newkeys(256)
# 加密， 解密函数


def encode_email(email, salt):
    email = email[1:10].encode("utf8")
    crypto = rsa.encrypt(salt + email, pubkey)
    return crypto


def decode_email(crypto):
    email = rsa.decrypt(crypto, privkey)
    return email