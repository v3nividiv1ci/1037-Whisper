import pymysql
import mysql_ctrl.mysql_pool as mysql_pool


def recreate_post():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS POST")
    sql = """CREATE TABLE IF NOT EXISTS `POST`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `POST_CONTENT` VARCHAR(200) NOT NULL,
	    `EMAIL_CRYPTO` BLOB,
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
        `COMMENT_CONTENT` VARCHAR(200) NOT NULL,
       `EMAIL_CRYPTO` BLOB,
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
        `C_COMMENT_CONTENT` VARCHAR(200) NOT NULL,
        `EMAIL_CRYPTO` BLOB,
        `TIME` TIMESTAMP,
        `COMMENT_ID` INT UNSIGNED,
        `POST_ID` INT UNSIGNED,
        PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)


def recreate_blacklist():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS BLACKLIST")
    sql = """CREATE TABLE IF NOT EXISTS `BLACKLIST`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `EMAIL_HASH` BIGINT(20),
	    PRIMARY KEY ( `ID`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)

#
# def admin():
#     conn, cursor = mysql_pool.create_conn()
#     cursor.execute("DROP TABLE IF EXISTS ADMINS")
#     sql = """CREATE TABLE IF NOT EXISTS `ADMINS`(
#             `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
#             `ADMIN_HASH` VARCHAR(40) NOT NULL,
#     	    PRIMARY KEY ( `ID` )
#         )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
#     cursor.execute(sql)
#     conn.commit()
#     mysql_pool.close_conn(conn, cursor)

def recreate_elective():
    conn, cursor = mysql_pool.create_conn()
    cursor.execute("DROP TABLE IF EXISTS ELECTIVE")
    sql = """CREATE TABLE IF NOT EXISTS `ELECTIVE`(
        `ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `SIGN` INT UNSIGNED NOT NULL,
        `FORM` INT UNSIGNED NOT NULL,
	    `HW` INT UNSIGNED NOT NULL,
        `FISH` INT UNSIGNED NOT NULL,
        `GENERAL` INT UNSIGNED NOT NULL,
        `COMMENT` VARCHAR(200) NOT NULL,
        `TIME` TIMESTAMP,
        `LECTURE` VARCHAR(40) NOT NULL,
        PRIMARY KEY ( `ID` )
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
    cursor.execute(sql)
    conn.commit()
    mysql_pool.close_conn(conn, cursor)