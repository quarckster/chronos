import MySQLdb
import sys
from config_parser import cfg

try:
    conn = MySQLdb.connect(host=cfg.db.host,
                           user=cfg.db.user,
                           passwd=cfg.db.password,
                           db=cfg.db.name)
except MySQLdb.Error as e:
    sys.exit(1)