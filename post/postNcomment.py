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


def comment(p_comment, token, conn, post_id):
    cursor = conn.cursor()
    email = jwt.decode(token, config.key)
    # 在回帖表中插入回帖
    sql = "INSERT INTO P_COMMENT VALUES(NULL, NULL, NULL, %s, %s, NOW(), %s)"
    insert = cursor.execute(sql, (p_comment, email, post_id))
    # 获得这条回帖的id
    id = cursor.lastrowid
    # 总帖存在，1
    query_01 = cursor.execute("SELECT * FROM POST WHERE ID=%s").formate(post_id)
    # 没有评论，0；有评论，1
    query_02 = cursor.execute("SELECT COMMENT_ID FROM POST WHERE ID=post_id")
    if query_01 and (not query_02):
        # 如果总帖存在并且没有评论，更新对应总帖的comment_id
        sql = "UPDATE POST SET COMMENT_ID=id, LAST_UPDATE=NOW() WHERE ID=post_id"
        update = cursor.execute(sql)
    elif query_01 and query_02:
        # 如果总贴存在并且有评论
        comment_id = cursor.fetchone()[0]
        cursor.execute("SELECT NEXT_ID FROM P_COMMENT WHERE id={}").format(comment_id)
