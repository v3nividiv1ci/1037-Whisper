import os

import redis
from flask import Flask
from flask import request
import jwt

import post.postNcomment as pNc
import validation.autosend_email as autosend_mail
import validation.gen_token as gen_token
import validation.redis_control as redis_control
import validation.validate as validate
import love_death_elective.comment_elective as comment_elective
import mysql_ctrl.recreate_tbl as recreate_tbl
import config


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
    # recreate_tbl.recreate_post()
    # recreate_tbl.recreate_p_comment()
    # recreate_tbl.recreate_c_comment()
    # recreate_tbl.recreate_blacklist()
    recreate_tbl.recreate_elective()



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
                message = "200 - email successfully sent! >< plz check it in 817 sec"
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
            if gen_token.authentication(token) and not pNc.if_ban(token):
                c_post = request.json.get("post")
                print(c_post, flush=True)
                # return "200"
                # if pNc.post(c_post, token, conn):
                if pNc.post(c_post, token):
                    return dict(success=True, message="200 - Post successfully sent.")
                else:
                    return dict(success=False, message="post error.", errorCode=4)
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 楼
    @app.route("/v1/comment", methods=["POST"])
    def comment():
        if request.method == "POST":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                post_id = request.args.get("post_id")
                print("post_id is", post_id)
                p_comment = request.json.get("content")
                status = pNc.comment(p_comment, token, post_id)
                if status == 1:
                    return dict(success=True, message="200 - Comment successfully sent.")
                elif status == 2:
                    return dict(success=False, message="404 - post not found", errorCode=5)
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 楼中楼
    @app.route("/v1/reply", methods=["POST"])
    def reply():
        if request.method == "POST":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                comment_id = request.args.get("comment_id")
                c_comment = request.json.get("content")
                status = pNc.reply(c_comment, token, comment_id)
                if status == 1:
                    return dict(success=True, message="200 - Reply successfully sent.")
                elif status == 2:
                    return dict(success=False, message="404 - post not found", errorCode=5)
                else:
                    return dict(success=False, message="404 - comment not found", errorCode=6)
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 首页帖子列表，列出最近20条帖子
    @app.route("/v1/view/all")
    def view_all():
        if request.method == "GET":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                post_list = pNc.get_recent20_post()
                return dict(success=True, message="200", posts=post_list)
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 删除post
    @app.route("/v1/delete/post", methods=["DELETE"])
    def delete_post():
        if request.method == "DELETE":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                post_id = request.args.get("post_id")
                pNc.delete(post_id, "POST", "ID")
                pNc.delete(post_id, "P_COMMENT", "POST_ID")
                pNc.delete(post_id, "C_COMMENT", "POST_ID")
                return dict(success=True, message="200")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 删除comment
    @app.route("/v1/delete/comment", methods=["DELETE"])
    def delete_comment():
        if request.method == "DELETE":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                comment_id = request.args.get("comment_id")
                pNc.delete(comment_id, "P_COMMENT", "ID")
                pNc.delete(comment_id, "C_COMMENT", "COMMENT_ID")
                return dict(success=True, message="200")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 删除reply
    @app.route("/v1/delete/reply", methods=["DELETE"])
    def delete_something():
        if request.method == "DELETE":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                reply_id = request.args.get("reply_id")
                pNc.delete(reply_id, "C_COMMENT", "ID")
                return dict(success=True, message="200")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 通过链接访问单条帖子，不需要鉴权
    @app.route("/v1/view")
    def view_post():
        if request.method == "GET":
            post_id = request.args.get("post_id")
            post = pNc.get_post(post_id)
            return dict(success=True, message = "200", post=post)

    # 封禁账号
    @app.route("/v1/ban", methods=["POST"])
    def ban():
        if request.method == "POST":
            token = request.json.get("token")
            if gen_token.if_admin(token):
                black_email = request.json.get("black_email")
                if pNc.ban(black_email):
                    return dict(success=True, message="200")
                else:
                    return dict(success=False, message="Already banned.")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    # 解封账号
    @app.route("/v1/unban", methods=["DELETE"])
    def unban():
        if request.method == "DELETE":
            token = request.json.get("token")
            if gen_token.if_admin(token):
                unban_id = request.json.get("unban_id")
                if pNc.unban(unban_id):
                    return dict(success=True, message="200")
                else:
                    return dict(success=False, message="Already unbanned.")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)

    @app.route("/v1/love_death_elective", methods=["POST"])
    def love_death_elective():
        if request.method == "POST":
            # 先鉴权
            token = request.json.get("token")
            if gen_token.authentication(token) and not pNc.if_ban(token):
                lecture = request.args["lecture"]
                if_sign, test_form, if_hw, if_touch_fish, general, comment =\
                    request.json["sign"], request.json["test"], request.json["hw"], request.json["fish"], request.json["general"], request.json["comment"]
                if comment_elective.comment_elective(if_sign, test_form, if_hw, if_touch_fish, lecture, comment, general):
                    return dict(success=True, message="200")
            else:
                return dict(success=False, message="Invalid token.", errorCode=3)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
