import MySQLdb
import MySQLdb.cursors
from config_parser import cfg

class DB:
    conn = None

    def connect(self):
        self.conn = MySQLdb.connect(host=cfg.db.host,
                                    user=cfg.db.user,
                                    passwd=cfg.db.password,
                                    db=cfg.db.name)

    def query(self, sql, cursorclass=MySQLdb.cursors.DictCursor):
        try:
            with self.conn:
                cursor = self.conn.cursor(cursorclass=cursorclass)
                cursor.execute(sql)
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            with self.conn:
                cursor = self.conn.cursor(cursorclass=cursorclass)
                cursor.execute(sql)
        return cursor