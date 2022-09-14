"""Глобальные константы"""

import logging

# Текущий уровень логирования
LEVEL_LOGGING_SET = logging.DEBUG
# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
SENDER = 'sender'
ACCOUNT_NAME = 'account_name'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
SEND = 'send'
RESPONSE = 'response'
ERROR = 'error'
TEXT = 'text'
ACCEPT_MODE = 'accept_mode'
SEND_MODE = 'send_mode'
EXIT = 'exit'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}