import os

import redis
from flask import Flask
from flask import request

import post.postNcomment as pNc
import validation.autosend_email as autosend_mail
import validation.gen_token as gen_token
import validation.redis_control as redis_control
import validation.validate as validate


def create_app(test_config=None):
    # 创建app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    # 连接数据库 redis
    # 我把这个放到主函数里，可能比较符合" 使用 connection pool 来管理对一个 redis server 的所有连接，避免每次建立、释放连接的开销"的初衷？（
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    print(pool)
    # 连接数据库mysql
    # conn = mysql_ctrl.connect_db()
    # 建立连接池 (这段是我抄的）


    @app.route("/v1/validation")
    def validation():
        if request.method == "GET":
            email = request.json.get("email")
            # もっとちゃんと応えてよ --「ヒバナ」
            if email == "hibana@hust.edu.cn":
                return dict(success=False, message="もっとちゃんと応えてよww")
            elif validate.validate_email(email):
                # return "valid email"
                v_code = redis_control.generate_vcode(pool, email)
                autosend_mail.send_email(email, v_code)
                message = "email successfully sent! >< plz check it in 817 sec"
                return dict(success=True, message=message)
            else:
                return dict(success=False, message="Invalid email.", errorCode=1)

    @app.route("/v1/email_code")
    def email_code():
        if request.method == "GET":
            email = request.json.get("email")
            c_code = request.json.get("c_code")
            if redis_control.verify_redis(pool, email, c_code):
                token = gen_token.generate_token(email)
                # "Successfully validated! Token already allocated. Welcome to 1037-Whisper! "
                return dict(success=True, token=token, message="200")
            else:
                # "Wrong or expelled CAPTCHA, plz resend ur request or resend ur email address to get a new CAPTCHA."
                return dict(success=False, message="wrong or expelled CAPTCHA", errorCode=2)

    @app.route("/v1/post", methods=["POST"])
    def post():
        if request.method == "POST":
            # 先鉴权
            token = request.json.get("token")
            # print(token, flush=True)
            if gen_token.authentication(token):
                c_post = request.json.get("post")
                print(c_post, flush=True)
                # return "200"
                # if pNc.post(c_post, token, conn):
                if pNc.post(c_post, token):
                    return dict(success=True, message="Post successfully sent.")
                else:
                    return dict(success=False, message="post error.", errorCode=4)
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    @app.route("/v1/comment", methods=["POST"])
    def comment():
        if request.method == "POST":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token):
                post_id = request.args.get("post_id")
                print("post_id is", post_id)
                p_comment = request.json.get("comment")
                pNc.comment(p_comment, token, post_id)
                return dict(success=True, message="Comment successfully sent.")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)


    @app.route("/v1/post_")
    def view_post():
        if request.method == "GET":
            # 先鉴权
            token = request.json.get("token")
            POST_ID = request.args.get("post")
            if gen_token.authentication(token):
                pass
                return dict(success=True, message=" ")
            else:
                # 怎么才能不允许非登陆态用户无法显示树洞首页的帖子列表，以及其他后续功能 ？
                return dict(success=False, message=" .", errorCode=3)
    # @app.route()

    @app.route("/v1/test", methods=["POST"])
    def test():
        if request.method == "POST":
            # 先鉴权
            # token = request.json.get("token")
            return "200"

    # 断开数据库连接
    # mysql_ctrl.exit_db(conn)
    return app


if __name__ == '__main__':
    app = create_app()
