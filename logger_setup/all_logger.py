import logging


logger = logging.getLogger("myapp")
logger_db=logging.getLogger("mydb")

logger_db.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s - %(name)s::::%(message)s'
)

json_log_path = "logger_setup/test.log"
db_log_path = "logger_setup/dblogs.log"
filehandler = logging.FileHandler(json_log_path)
filehandler2 = logging.FileHandler(db_log_path)

filehandler.setFormatter(formatter)
filehandler2.setFormatter(formatter)

logger_db.addHandler(filehandler2)
logger.addHandler(filehandler)


consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)


logger.addHandler(consolehandler)
logger_db.addHandler(consolehandler)


logger.propagate = False
logger_db.propagate=False
