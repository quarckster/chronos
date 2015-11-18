import MySQLdb
import sys
from config_parser import cfg
from root_logger import root_logger

MySQLdb_error = MySQLdb.Error
# Connecting to DB
try:
    conn = MySQLdb.connect(host=cfg.db.host,
                           user=cfg.db.user,
                           passwd=cfg.db.password,
                           db=cfg.db.name)
except MySQLdb_error as e:
    root_logger.exception("Cannot connect to DB: %s" % e)
    sys.exit(1)