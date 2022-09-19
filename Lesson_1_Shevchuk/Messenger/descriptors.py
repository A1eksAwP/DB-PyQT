import logging
from logs.config import server_log_config
from common.variables import DEFAULT_PORT, MIN_AVAILABLE_PORT, MAX_AVAILABLE_PORT

LOGGER = logging.getLogger('server')


class PortVerifier:
    """
    Дескриптор, верифицирующий номер подключаемого порта
    """
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, port):
        if not MIN_AVAILABLE_PORT <= port <= MAX_AVAILABLE_PORT:
            LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{port}. Допустимы адреса с {MIN_AVAILABLE_PORT} до {MAX_AVAILABLE_PORT}.'
                            )
        instance.__dict__[self.name] = port
