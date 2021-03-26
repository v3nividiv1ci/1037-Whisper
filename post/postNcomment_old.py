import pymysql
import config
import jwt
import mysql_ctrl.mysql_pool as mysql_pool
import encodeNdecode.rsa_key as rsa_key

# def email_index(email):
#     conn, cursor = mysql_pool.create_conn()
#     sql = "SELECT * FROM EMAIL WHERE EMAIL='{}'".format(email)
#     cursor.execute(sql)
#     test = cursor.fetchone()
#     if not test:
#         sql = "INSERT INTO EMAIL VALUES(NULL, '{}')".format(email)
#         cursor.execute(sql)
#         email_id = cursor.lastrowid
#     else:
#         email_id = test[0]
#     conn.commit()
#     mysql_pool.close_conn(conn, cursor)
#     return email_id


def post(c_post, token):
    # 接受了post的内容以及token
    # 要将其存入数据库
    conn, cursor= mysql_pool.create_conn()
    # cursor.scroll(0, 'absolute')
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    # print(email)
    # email_id = email_index(email)
    sql = "INSERT INTO POST VALUES(NULL, NULL, NULL, %s, NULL, NOW(), NOW())"
    cursor.execute(sql, c_post)
    id = cursor.lastrowid
    email_crypto = rsa_key.encode_email(email, id)
    sql = "UPDATE POST SET EMAIL_CRYPTO=%s WHERE ID=%s".format(email_crypto, id)
    cursor.execute(sql)
    # print(id)
    # cursor.execute("SELECT * FROM POST")
    if id != 1:
        # 如果不是第一条帖子
        sql = "UPDATE POST SET NEXT_ID=%s WHERE ID=%s "
        cursor.execute(sql, (id, id - 1))
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return True
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def comment(p_comment, token, post_id):
    # 两个表，两个游标
    conn_c, cursor_c= mysql_pool.create_conn()
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
    sql = "INSERT INTO P_COMMENT VALUES(NULL, NULL, NULL, %s, %s, NOW(), %s)"
    cursor_c.execute(sql, (p_comment, email_crypto, post_id))
    # 获得这条回帖的id
    cid = cursor_c.lastrowid
    # query_01是对应总帖的索引，索引是否为null与是否存在总帖幂等
    query_01 = cursor_p.fetchone()[0]
    # print("query01 is:", query_01)
    sql = "SELECT COMMENT_ID FROM POST WHERE ID={}".format(post_id)
    cursor_p.execute(sql)
    # query_02是对应总帖的comment_id（第一条评论的索引），为null与没有评论幂等
    query_02 = cursor_p.fetchone()[0]
    if not query_02:
        # 如果总帖存在并且没有评论，更新对应总帖的comment_id
        sql = "UPDATE POST SET COMMENT_ID={} WHERE ID={}".format(cid, post_id)
        cursor_p.execute(sql)
    elif query_02:
        # 如果总贴存在并且有评论，那就在P_COMMENT里面找到这句评论，并且沿着next_id一直往下找，直到next_id为空，在这里插入新评论
        # 即：将这条的next_id设置为现在的（参见post）
        # 查找最后一条p_comment
        comment_next = query_02
        while comment_next:
            sql = "SELECT ID, NEXT_ID FROM P_COMMENT WHERE ID={}".format(comment_next)
            cursor_c.execute(sql)
            # comment_now 这条评论的id, comment_next 下条评论的id
            comment_now, comment_next = cursor_c.fetchone()
        # 查找到了最后一条评论，将其next_id设为cid
        # comment_now 没插入之前最后一条评论的id
        sql = "UPDATE P_COMMENT SET NEXT_ID={} WHERE ID={}".format(cid, comment_now)
        cursor_c.execute(sql)
    # 更新POST中对应总帖最后一次更新的时间
    sql = "UPDATE POST SET LAST_UPD=NOW() WHERE ID={}".format(post_id)
    cursor_p.execute(sql)
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_c, cursor_c)
    mysql_pool.close_conn(conn_p, cursor_p)
    return 1


def reply(c_comment, token, comment_id):
    # 三个表，三个游标
    conn_po, cursor_po = mysql_pool.create_conn()
    conn_c, cursor_c = mysql_pool.create_conn()
    conn_p, cursor_p = mysql_pool.create_conn()
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    # 查找楼中楼回复的楼所对应的总帖 post_id
    sql = "SELECT POST_ID FROM P_COMMENT WHERE ID={}".format(comment_id)
    # 如果查找父级为空(不用回滚?)
    if not cursor_p.execute(sql):
        mysql_pool.close_conn(conn_po, cursor_po)
        mysql_pool.close_conn(conn_c, cursor_c)
        mysql_pool.close_conn(conn_p, cursor_p)
        return 3
    # 如果👴（总帖）是🈳️的
    post_id = cursor_p.fetchone()[0]
    if not post_id:
        mysql_pool.close_conn(conn_po, cursor_po)
        mysql_pool.close_conn(conn_c, cursor_c)
        mysql_pool.close_conn(conn_p, cursor_p)
        return 2
    # 在楼中楼表中插入楼中楼
    email_crypto = rsa_key.encode_email(email, post_id)
    sql = "INSERT INTO C_COMMENT VALUES(NULL, NULL, %s, %s, NOW(), %s, %s)"
    cursor_c.execute(sql, (c_comment, email_crypto, comment_id, post_id))
    # 获得这条楼中楼的id
    cid = cursor_c.lastrowid
    sql = "SELECT * FROM P_COMMENT WHERE ID={}".format(comment_id)
    cursor_p.execute(sql)
    # query_01是对应楼的索引，索引是否为null与是否存在楼幂等
    query_01 = cursor_p.fetchone()[0]
    # print("query01 is:", query_01)
    sql = "SELECT P_COMMENT_ID FROM P_COMMENT WHERE ID={}".format(comment_id)
    cursor_p.execute(sql)
    # query_02是对应总帖的comment_id（第一条评论的索引），为null与没有评论幂等
    query_02 = cursor_p.fetchone()[0]
    if not query_02:
        # 如果楼存在并且没有楼中楼，更新对应楼的p_comment_id
        sql = "UPDATE P_COMMENT SET P_COMMENT_ID={} WHERE ID={}".format(cid, comment_id)
        cursor_p.execute(sql)
    elif query_02:
        # 如果楼存在并且有楼中楼，那就在C_COMMENT里面找到这个楼中楼，并且沿着next_id一直往下找，直到next_id为空，将其更改为cid
        # 即：将这条的next_id设置为现在的（参见post）
        # 查找最后一条c_comment
        comment_next = query_02
        while comment_next:
            sql = "SELECT ID, NEXT_ID FROM C_COMMENT WHERE ID={}".format(comment_next)
            cursor_c.execute(sql)
            # comment_now 这条评论的id, comment_next 下条评论的id
            comment_now, comment_next = cursor_c.fetchone()
        # 查找到了最后一条评论，将其next_id设为cid
        # comment_now 没插入之前最后一条评论的id
        sql = "UPDATE C_COMMENT SET NEXT_ID={} WHERE ID={}".format(cid, comment_now)
        cursor_c.execute(sql)
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
    conn_e, cursor_e = mysql_pool.create_conn()
    # 反向排序
    sql = "SELECT ID, POST_CONTENT, EMAIL_ID, LAST_UPD FROM POST ORDER BY LAST_UPD DESC"
    cursor_p.execute(sql)
    posts = cursor_p.fetchmany(20)
    for post in posts:
        print(post)
    post_list = []
    for post in posts:
        post_dict = {}
        post_dict.update({"id": post[0], "content": post[1], "email": post[2], "last_upd": post[3]})
        post_list.append(post_dict)
    # print("len", len(post_list))
    conn_p.commit()
    conn_e.commit()
    mysql_pool.close_conn(conn_e, cursor_e)
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
    print("post_content is", post_content)
    post.append(post_content)
    # 查找对应post_id的comment
    sql = "SELECT * FROM P_COMMENT WHERE POST_ID = {}".format(post_id)
    cursor_p.execute(sql)
    comment_content = cursor_p.fetchall()
    print("comment_content is", comment_content)
    post.append(comment_content)
    # 查找对应post_id的reply
    sql = "SELECT * FROM C_COMMENT WHERE POST_ID = {}".format(post_id)
    cursor_c.execute(sql)
    reply_content = cursor_c.fetchall()
    print("reply_content is:", reply_content)
    post.append(reply_content)
    conn_po.commit()
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_po, cursor_po)
    mysql_pool.close_conn(conn_c, cursor_c)
    mysql_pool.close_conn(conn_p, cursor_p)
    return post


def delete_post(post_id):
    conn, cursor = mysql_pool.create_conn()
    sql = "DELETE FROM POST WHERE ID = {}".format(post_id)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def delete_comment(comment_id):
    conn, cursor = mysql_pool.create_conn()
    sql = "DELETE FROM C_COMMENT WHERE ID = {}".format(comment_id)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def delete_reply(reply_id):
    conn, cursor = mysql_pool.create_conn()
    sql = "DELETE FROM C_COMMENT WHERE ID={}".format(reply_id)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True

