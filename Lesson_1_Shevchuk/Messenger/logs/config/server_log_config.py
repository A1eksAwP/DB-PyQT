import logging
import logging.handlers as log_handle
import os
import sys
from common.variables import LEVEL_LOGGING_SET

# создаём формировщик логов (formatter):
SERVER_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s'
)

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '../log_files/server.log')

# создаём потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_FILE = log_handle.TimedRotatingFileHandler(
    PATH,
    encoding='utf8',
    interval=1,
    when='D'
)
LOG_FILE.setFormatter(SERVER_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LEVEL_LOGGING_SET)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Тест критической ошибки')
    LOGGER.error('Тест ошибки')
    LOGGER.debug('Тест отладочной информации')
    LOGGER.info('Тест информационного сообщения')
