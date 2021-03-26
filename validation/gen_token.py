import jwt
import time
import config
import validation.validate as validate


def generate_token(email):
    # 失效时间
    exp = int(time.time()) + 86400 * 114
    # JSON数据
    payload = {"exp": exp, "user_email": email}
    # 生成token
    token = jwt.encode(payload, config.key)
    return token


def authentication(token):
    # 最开始写的时候没有注意返回值的类型，debug了好久（（
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    email_hash = hash(email)
    if validate.validate_email(email) and (not email_hash):
        return True
    else:
        return False