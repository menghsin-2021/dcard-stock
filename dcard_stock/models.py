import pymysql.cursors

# Connect to the database
import pymysql



def connect_db(host, user, password, db_name=None, port=3306):
    try:
        connect_db = pymysql.connect(host=host,
                                     port=port,
                                     user=user,
                                     password=password,
                                     database=db_name,)
        return connect_db
    except pymysql.MySQLError as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
        return None

def create_db(cursor, DBNAME):
    # create database
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4' ".format(DBNAME)
        )
    except Exception as e:
        print("Exeception occured:{}".format(e))

    # use database
    try:
        cursor.execute("USE {}".format(DBNAME))
    except Exception as e:
        print("Exeception occured:{}".format(e))

    return cursor

def create_tb(cursor, TABLES, TBNAME_1=None, TBNAME_2=None):
    # posts table
    if TBNAME_1:
        TABLES[TBNAME_1] = ("CREATE TABLE IF NOT EXISTS {}( \
            `articleID` INT(11) COLLATE utf8mb4_bin NOT NULL, \
            `author` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `forum_alias` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `created_at_utc` DATETIME DEFAULT 0 NOT NULL, \
            `created_at_tw` DATETIME DEFAULT 0 NOT NULL, \
            `time_string` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `title` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `topics` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `content` TEXT COLLATE utf8mb4_bin NOT NULL, \
            `gender` CHAR(1) COLLATE utf8mb4_bin NOT NULL, \
            `react_count` INT(11) COLLATE utf8mb4_bin NOT NULL, \
            `comment_count` INT(11) COLLATE utf8mb4_bin NOT NULL, \
            PRIMARY KEY (`articleID`) \
            )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;".format(TBNAME_1))

    if TBNAME_2:
        TABLES[TBNAME_2] = ("CREATE TABLE IF NOT EXISTS {}( \
            `reactionID` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `articleID` INT(11) COLLATE utf8mb4_bin NOT NULL, \
            `author` VARCHAR(255) COLLATE utf8mb4_bin NOT NULL, \
            `created_at_utc` DATETIME DEFAULT 0 NOT NULL, \
            `created_at_tw` DATETIME DEFAULT 0 NOT NULL, \
            `content` TEXT COLLATE utf8mb4_bin NOT NULL, \
            `like_count` INT(11) COLLATE utf8mb4_bin NOT NULL, \
            PRIMARY KEY (`reactionID`) \
            )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;".format(TBNAME_2))

    # articles table
    # TABLES[TBNAME] = ("CREATE TABLE IF NOT EXISTS {}( \
    #         `ID` int(11) COLLATE utf8mb4_bin NOT NULL AUTO_INCREMENT, \
    #         `articleID` int(11) COLLATE utf8mb4_bin NOT NULL, \
    #         PRIMARY KEY (`ID`) \
    #         )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;".format(TBNAME))

    # uff8mb4才允許中文

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
            print("OK")
        except Exception as e:
            print("Exeception occured:{}".format(e))










