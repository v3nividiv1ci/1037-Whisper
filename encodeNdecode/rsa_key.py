import rsa

# 读取公钥和私钥
with open('rsa_keys/public.pem', 'rb') as publickfile:
    p = publickfile.read()
pubkey = rsa.PublicKey.load_pkcs1(p)

with open('rsa_keys/private.pem', 'rb') as privatefile:
    p = privatefile.read()
privkey = rsa.PrivateKey.load_pkcs1(p)
# (pubkey, privkey) = rsa.newkeys(256)
# 加密， 解密函数


def encode_email(email, salt):
    email = email[1:10].encode("utf8")
    salt = salt.encode("utf8")
    crypto = rsa.encrypt(salt + email, pubkey)
    # crypto = str(crypto, encoding="utf-16")
    # crypto = str(crypto, encoding="ISO-8859-1")
    return crypto


def decode_email(crypto):
    # crypto = bytes(crypto, encoding="utf16")
    email = rsa.decrypt(crypto, privkey)
    email = bytes(email, encoding="utf8")
    return email