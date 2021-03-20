from flask import Flask
from flask import request
import string
import redis
import os
import validation.validate as validate
import validation.autosend_email as autosend_mail
import validation.redis_control as redis_control


def create_app(test_config=None):
    # 创建app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    # 我把这个放到主函数里，可能比较符合" 使用 connection pool 来管理对一个 redis server 的所有连接，避免每次建立、释放连接的开销"的初衷？（
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)

    @app.route('/v1/validation')
    def validation():
        if request.method == "GET":
            print(request.json)
            email = request.json.get("email")
            if validate.validate_email(email):
                # return "valid email"
                v_code = redis_control.generate_vcode(pool)
                autosend_mail.send_email(email, v_code)
            else:
                return "Invalid email, plz try again."

    @app.route('/v1/email_code')
    def email_code():
        if request.method == "GET":
            print(request.json)

    return app


if __name__ == '__main__':
    app = create_app()