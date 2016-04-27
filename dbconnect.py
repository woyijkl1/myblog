import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "yrd199676",
                           db = "pythonprogramming")
    c = conn.cursor()

    return c, conn
		