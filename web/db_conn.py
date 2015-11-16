import MySQLdb
import MySQLdb.cursors
from config_parser import cfg

class DB:
    conn = None

    def connect(self):
        self.conn = MySQLdb.connect(host=cfg.db.host,
                                    user=cfg.db.user,
                                    passwd=cfg.db.password,
                                    db=cfg.db.name,
                                    cursorclass=MySQLdb.cursors.DictCursor)

    def query(self, sql):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql)
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor

db = DB()