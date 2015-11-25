import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from chronos.lib.config_parser import cfg

log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s",
                                  "%Y-%m-%d %H:%M:%S")
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
rotate_logs_handler = TimedRotatingFileHandler(cfg.files.log_path, when="midnight", backupCount=3)
rotate_logs_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)
root_logger.addHandler(rotate_logs_handler)