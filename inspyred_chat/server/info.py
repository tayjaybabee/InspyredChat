from appdirs import user_config_dir
from inspy_logger import LEVELS as LOG_LEVELS
from pathlib import Path

PROG = "SimpleChatServer"
AUTHOR = 'Inspyre-Softworks'

DEFAULT_CONFIG_DIR = Path(user_config_dir(PROG, appauthor=AUTHOR))
CONFIG_FILE_NAME = 'inspyredchat'
CONFIG_FILE_EXTENSION = 'conf'


DEFAULT_PORT = 85855
