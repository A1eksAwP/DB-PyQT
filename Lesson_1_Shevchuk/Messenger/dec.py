import sys
import logging
from logs.config import server_log_config, client_log_config
import inspect

ls = logging.getLogger('server')
lc = logging.getLogger('client')
LOGGER = ls if sys.argv[0].find('client') == -1 else lc


class Log:

    def __call__(self, self_func):

        def log_process(*args, **kwargs):
            result = self_func(*args, **kwargs)
            LOGGER.info(f"Вызвана функция: {self_func.__name__} с аргументами {args}, {kwargs}. "
                        f"Вызвано модулем: {self_func.__module__} "
                        f"из функции: {inspect.stack()[1][3]}", stacklevel=2)
            return result

        return log_process

