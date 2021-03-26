import random
import string
import redis


def generate_vcode(pool, email):
    # 生成八位随机验证码
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    # 存入redis，设置过期时间
    r = redis.Redis(connection_pool=pool)
    r.set(email, ran_str, ex=817)
    return ran_str


def delete_vcode(pool, email):
    r = redis.Redis(connection_pool=pool)
    r.delete(email)
    # 如果已经验证，删除验证码


def verify_redis(pool, email, c_code):
    r = redis.Redis(connection_pool=pool)
    # 验证邮箱和验证码是否匹配，过期none了就直接和不匹配返回一样的
    if r.get(email) == c_code:
        delete_vcode(pool, email)
        return True
    return False
