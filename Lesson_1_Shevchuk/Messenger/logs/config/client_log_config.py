import logging
import os
import sys
from common.variables import LEVEL_LOGGING_SET

# создаём формировщик логов (formatter):
CLIENT_FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s'
)

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '../log_files/client.log')

# создаём потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LEVEL_LOGGING_SET)

# отладка
if __name__ == '__main__':
    LOGGER.critical('Тест критической ошибки')
    LOGGER.error('Тест ошибки')
    LOGGER.debug('Тест отладочной информации')
    LOGGER.info('Тест информационного сообщения')
