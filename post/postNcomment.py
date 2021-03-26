import pymysql
import config
import jwt
import mysql_ctrl.mysql_pool as mysql_pool
import encodeNdecode.rsa_key as rsa_key


def post(c_post, token):
    conn, cursor = mysql_pool.create_conn()
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    sql = "INSERT INTO POST VALUES(NULL, %s, NULL, NOW(), NOW())"
    cursor.execute(sql, c_post)
    id = cursor.lastrowid
    email_crypto = rsa_key.encode_email(email, id)
    sql = "UPDATE POST SET EMAIL_CRYPTO={} WHERE ID={}".format(email_crypto, id)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def comment(p_comment, token, post_id):
    # 两个表，两个游标
    conn_c, cursor_c = mysql_pool.create_conn()
    conn_p, cursor_p = mysql_pool.create_conn()
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    email_crypto = rsa_key.encode_email(email, post_id)
    # 查找对应总帖
    sql = "SELECT * FROM POST WHERE ID={}".format(post_id)
    # 如果查找父级为空
    if not cursor_p.execute(sql):
        conn_c.rollback()
        mysql_pool.close_conn(conn_c, cursor_c)
        mysql_pool.close_conn(conn_p, cursor_p)
        return 2
    # 在回帖表中插入回帖
    sql = "INSERT INTO P_COMMENT VALUES(NULL, %s, %s, NOW(), %s)"
    cursor_c.execute(sql, (p_comment, email_crypto, post_id))
    sql = "UPDATE POST SET LAST_UPD=NOW() WHERE ID={}".format(post_id)
    cursor_p.execute(sql)
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_c, cursor_c)
    mysql_pool.close_conn(conn_p, cursor_p)
    return 1


def reply(c_comment, token, comment_id):
    conn_po, cursor_po = mysql_pool.create_conn()
    conn_c, cursor_c = mysql_pool.create_conn()
    conn_p, cursor_p = mysql_pool.create_conn()
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    # 查找楼中楼回复的楼所对应的总帖 post_id
    sql = "SELECT POST_ID FROM P_COMMENT WHERE ID={}".format(comment_id)
    # 如果查找👨父级为空(不用回滚?)
    if not cursor_p.execute(sql):
        mysql_pool.close_conn(conn_po, cursor_po)
        mysql_pool.close_conn(conn_c, cursor_c)
        mysql_pool.close_conn(conn_p, cursor_p)
        return 3
    # 如果👴（总帖）or_p.fetchone()[0]
    post_id = cursor_p.fetchone()[0]
    if not post_id:
        mysql_pool.close_conn(conn_po, cursor_po)
        mysql_pool.close_conn(conn_c, cursor_c)
        mysql_pool.close_conn(conn_p, cursor_p)
        return 2
    # 在楼中楼表中插入楼中楼
    email_crypto = rsa_key.encode_email(email, post_id)
    sql = "INSERT INTO C_COMMENT VALUES(NULL, %s, %s, NOW(), %s, %s)"
    cursor_c.execute(sql, (c_comment, email_crypto, comment_id, post_id))
    # 更新POST中对应总帖最后一次更新的时间
    sql = "UPDATE POST SET LAST_UPD=NOW() WHERE ID={}".format(post_id)
    cursor_po.execute(sql)
    # 更新总帖的最后更新时间
    conn_po.commit()
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_po, cursor_po)
    mysql_pool.close_conn(conn_c, cursor_c)
    mysql_pool.close_conn(conn_p, cursor_p)
    return 1


def get_recent10_post():
    conn_p, cursor_p = mysql_pool.create_conn()
    sql = "SELECT ID, POST_CONTENT, EMAIL_ID, LAST_UPD FROM POST ORDER BY LAST_UPD DESC"
    cursor_p.execute(sql)
    posts = cursor_p.fetchmany(20)
    # for post in posts:
    #     print(post)
    post_list = []
    for post in posts:
        post_dict = {}
        post_dict.update({"id": post[0], "content": post[1], "email": post[2], "last_upd": post[3]})
        post_list.append(post_dict)
    # print("len", len(post_list))
    conn_p.commit()
    mysql_pool.close_conn(conn_p, cursor_p)
    return post_list


def get_post(post_id):
    # 三个表，三个游标
    conn_po, cursor_po = mysql_pool.create_conn()
    conn_c, cursor_c = mysql_pool.create_conn()
    conn_p, cursor_p = mysql_pool.create_conn()
    post = []
    # 查找对应post_id的post
    sql = "SELECT * FROM POST WHERE ID = {}".format(post_id)
    cursor_po.execute(sql)
    post_content = cursor_po.fetchall()
    # print("post_content is", post_content)
    post.append(post_content)
    # 查找对应post_id的comment
    sql = "SELECT * FROM P_COMMENT WHERE POST_ID = {}".format(post_id)
    cursor_p.execute(sql)
    comment_content = cursor_p.fetchall()
    # print("comment_content is", comment_content)
    post.append(comment_content)
    # 查找对应post_id的reply
    sql = "SELECT * FROM C_COMMENT WHERE POST_ID = {}".format(post_id)
    cursor_c.execute(sql)
    reply_content = cursor_c.fetchall()
    # print("reply_content is:", reply_content)
    post.append(reply_content)
    conn_po.commit()
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_po, cursor_po)


def delete(id, table_name):
    conn, cursor = mysql_pool.create_conn()
    sql = "DELETE FROM " + table_name + " WHERE ID = {}".format(id)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def ban(email):
    conn, cursor = mysql_pool.create_conn()
    id_hash = hash(email[1:10])
    sql = "SELECT * FROM BLACKLIST WHERE EMAIL_HASH = {}".format(id_hash)
    if cursor.execute(sql):
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return False
    else:
        sql = "INSERT INTO BLACKLIST VALUES(NULL, %s)"
        cursor.execute(sql, id_hash)
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return True


def unban(id_num):
    conn, cursor = mysql_pool.create_conn()
    id_hash = hash(id_num)
    sql = "SELECT * FROM BLACKLIST WHERE EMAIL_HASH = {}".format(id_hash)
    if cursor.execute(sql):
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return False
    else:
        sql = "DELETE FROM BLACKLIST WHERE EMAIL_HASH = {}".format(id_hash)
        cursor.execute(sql)
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return True



def if_ban(token):
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    conn, cursor = mysql_pool.create_conn()
    id_hash = hash(email[1:10])
    sql = "SELECT * FROM BLACKLIST WHERE EMAIL_HASH = {}".format(id_hash)
    if cursor.execute(sql):
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return True
    else:
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return False