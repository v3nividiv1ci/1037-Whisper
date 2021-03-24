import pymysql
import config
# 发帖一个表，回帖一个表，楼中楼一个表, email一个表


def connect_db():
    conn = pymysql.connect(host="localhost", user="root", passwd=config.passwd, db=config.db, unix_socket="/tmp/mysql.sock")
    # cursor = conn.cursor()
    return conn


def exit_db(conn):
    cursor = conn.cursor()
    conn.commit()
    cursor.close()
    conn.close()