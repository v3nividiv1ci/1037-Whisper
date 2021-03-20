import random
import string
import redis


def generate_vcode(pool):
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    # 存入redis，设置过期时间
    r = redis.Redis(connection_pool=pool)
    pass
    return ran_str


def delete_vcode(pool):
    r = redis.Redis(connection_pool=pool)
    # 如果已经验证，删除验证码
    pass


def verify_redis(pool):
    r = redis.Redis(connection_pool=pool)
    # 验证邮箱和验证码是否匹配，过期none了就直接和不匹配返回一样吧？
    pass

