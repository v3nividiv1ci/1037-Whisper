import pymysql
import config
import jwt
import mysql_ctrl.mysql_pool as mysql_pool


def email_index(email):
    conn, cursor = mysql_pool.create_conn()
    sql = "SELECT * FROM EMAIL WHERE EMAIL='{}'".format(email)
    if not cursor.execute(sql):
        sql = "INSERT INTO EMAIL VALUES(NULL, '{}')".format(email)
        cursor.execute(sql)
    email_id = cursor.lastrowid
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return email_id


def post(c_post, token):
    # 接受了post的内容以及token
    # 要将其存入数据库
    conn, cursor= mysql_pool.create_conn()
    # cursor.scroll(0, 'absolute')
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    email_id = email_index(email)
    sql = "INSERT INTO POST VALUES(NULL, NULL, NULL, %s, %s, NOW(), NULL)"
    cursor.execute(sql, (c_post, email_id))
    id = cursor.lastrowid
    print(id)
    # cursor.execute("SELECT * FROM POST")
    if id != 1:
        # 如果不是第零条帖子
        sql = "UPDATE POST SET NEXT_ID=%s WHERE ID=%s "
        cursor.execute(sql, (id, id - 1))
        conn.commit()
        mysql_pool.close_conn(conn, cursor)
        return True
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True


def comment(p_comment, token, post_id):
    conn_c, cursor_c= mysql_pool.create_conn()
    conn_p, cursor_p = mysql_pool.create_conn()
    email = jwt.decode(token, config.key, algorithms=['HS256'])['user_email']
    email_id = email_index(email)
    # 在回帖表中插入回帖
    sql = "INSERT INTO P_COMMENT VALUES(NULL, NULL, NULL, %s, %s, NOW(), %s)"
    cursor_c.execute(sql, (p_comment, email_id, post_id))
    # 获得这条回帖的id
    cid = cursor_c.lastrowid
    # print("cursor_c.lastrowid is:", cid)
    # 总帖存在，1
    sql = "SELECT * FROM POST WHERE ID={}".format(post_id)
    cursor_p.execute(sql)
    # query_01是对应总帖的索引，索引是否为null与是否存在总帖幂等
    query_01 = cursor_p.fetchone()[0]
    # print("query01 is:", query_01)
    # 没有评论，0；有评论，1
    sql = "SELECT COMMENT_ID FROM POST WHERE ID={}".format(post_id)
    cursor_p.execute(sql)
    # query_02是对应总帖的comment_id（第一条评论的索引），为null与没有评论幂等
    query_02 = cursor_p.fetchone()[0]
    # print("query02 is:", query_02)
    if query_01 and (not query_02):
        # 如果总帖存在并且没有评论，更新对应总帖的comment_id
        sql = "UPDATE POST SET COMMENT_ID={}, LAST_UPD=NOW() WHERE ID={}".format(cid, post_id)
        cursor_p.execute(sql)
    elif query_01 and query_02:
        # 如果总贴存在并且有评论，那就在P_COMMENT里面找到这句评论，并且沿着next_id一直往下找，直到next_id为空，在这里插入新评论
        # 即：将这条的next_id设置为现在的（参见post）
        # 查找最后一条p_comment
        comment_next = query_02
        while comment_next:
            sql = "SELECT ID, NEXT_ID FROM P_COMMENT WHERE ID={}".format(comment_next)
            cursor_c.execute(sql)
            # comment_now 这条评论的id, comment_next 下条评论的id
            comment_now, comment_next = cursor_c.fetchone()
            # print("下一条评论的id是：", comment_next)
        # 查找到了最后一条评论，将其next_id设为cid
        # comment_now 没插入之前最后一条评论的id
        sql = "UPDATE P_COMMENT SET NEXT_ID={} WHERE ID={}".format(cid, comment_now)
        cursor_c.execute(sql)
    conn_c.commit()
    conn_p.commit()
    mysql_pool.close_conn(conn_c, cursor_c)
    mysql_pool.close_conn(conn_p, cursor_p)
