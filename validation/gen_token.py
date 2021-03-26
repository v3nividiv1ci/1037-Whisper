import jwt
import time
import config
import validation.validate as validate


def generate_token(email):
    # 失效时间
    exp = int(time.time()) + 86400 * 114
    # JSON数据
    # 生成token
    if email == "u202013878@hust.edu.cn" or "U202013878@hust.edu.cn":
        payload = {"exp": exp, "user_email": email, "admin": True}
    else:
        payload = {"exp": exp, "user_email": email, "admin": False}
    token = jwt.encode(payload, config.key)
    return token


def authentication(token):
    # 最开始写的时候没有注意返回值的类型，debug了好久（（
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    if validate.validate_email(email):
        return True
    else:
        return False


def if_admin(token):
    admin = jwt.decode(token, config.key, algorithms=['HS256'])['admin']
    if admin:
        return True
    else:
        return False