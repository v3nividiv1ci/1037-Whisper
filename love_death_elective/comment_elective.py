import pymysql
import mysql_ctrl.mysql_pool as mysql_pool


def comment_elective(if_sign, test_form, if_hw, if_touch_fish, lecture, comment, general):
    conn, cursor = mysql_pool.create_conn()
    sql = "INSERT INTO ELECTIVE VALUES(NULL, {}, {}, {}, {}, {}, '{}', NOW(), '{}')"\
        .format(if_sign, test_form, if_hw, if_touch_fish, general, comment, lecture)
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)
    return True
