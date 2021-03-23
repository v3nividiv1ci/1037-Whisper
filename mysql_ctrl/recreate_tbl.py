import pymysql
import mysql_ctrl.mysql_pool as mysql_pool


def recreate_post():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS POST")
    sql = """CREATE TABLE IF NOT EXISTS `POST`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `NEXT_ID` INT UNSIGNED,
	    `COMMENT_ID` INT UNSIGNED,
        `POST_CONTENT` VARCHAR(200) NOT NULL,
	    `EMAIL_ID` INT UNSIGNED,
        `TIME` TIMESTAMP,
        `LAST_UPD` TIMESTAMP,
        PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)


def recreate_p_comment():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS P_COMMENT")
    sql = """CREATE TABLE IF NOT EXISTS `P_COMMENT`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `NEXT_ID` INT UNSIGNED,
	    `P_COMMENT_ID` INT UNSIGNED,
        `COMMENT_CONTENT` VARCHAR(200) NOT NULL,
	    `EMAIL_ID` INT UNSIGNED,
        `TIME` TIMESTAMP,
        `POST_ID` INT UNSIGNED,
        PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)

def recreate_c_comment():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS C_COMMENT")
    sql = """CREATE TABLE IF NOT EXISTS `C_COMMENT`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `NEXT_ID` INT UNSIGNED,
        `C_COMMENT_CONTENT` VARCHAR(200) NOT NULL,
	    `EMAIL_ID` INT UNSIGNED,
        `TIME` TIMESTAMP,
        `COMMENT_ID` INT UNSIGNED,
        `POST_ID` INT UNSIGNED,
        PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)

def recreate_email():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS EMAIL")
    sql = """CREATE TABLE IF NOT EXISTS `EMAIL`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `EMAIL` VARCHAR(40) NOT NULL,
	    PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)