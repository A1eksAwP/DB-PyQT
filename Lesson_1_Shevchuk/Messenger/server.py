"""Программа-сервер"""

import socket
import select
import sys
import logging
import argparse
from logs.config import server_log_config
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_PORT, SEND, SENDER, TEXT, MAX_CONNECTIONS, \
    RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from common.utils import get_message, send_message
from dec import Log

# Инициализация серверного логера
SL = logging.getLogger('server')


class Server:
    name = "Server"

    def __init__(self):
        pass

    @staticmethod
    @Log()
    def process_client_message(message, messages_list, client, clients_list, names):

        SL.debug(f'Разбор сообщения: {message} от клиента')
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            # Иначе отдаём Bad request
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                clients_list.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif ACTION in message \
                and message[ACTION] == SEND \
                and TIME in message \
                and TEXT in message \
                and DESTINATION in message:
            messages_list.append(message)
            return
        # Если клиент выходит
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            clients_list.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос.'
            send_message(client, response)
            clients_list.remove(client)
            client.close()

    @staticmethod
    @Log()
    def process_message(message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names \
                and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            SL.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names \
                and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SL.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    @Log()
    def argument_parse(self):
        """Парсер аргументов коммандной строки"""
        my_arg = argparse.ArgumentParser()
        my_arg.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        my_arg.add_argument('-a', default='', nargs='?')
        namespace = my_arg.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        # проверка получения корректного номера порта для работы сервера.
        if not 1023 < listen_port < 65536:
            SL.critical(
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)
        return listen_address, listen_port

    def general(self):
        '''
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умолчанию.
        Сначала обрабатываем порт:
        server.py -p 8880 -a 192.168.0.107
        :return:
        '''

        listen_address, listen_port = self.argument_parse()

        SL.info(
            f'Запущен сервер, порт для подключений: {listen_port}, '
            f'адрес с которого принимаются подключения: {listen_address}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')

        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))
        transport.settimeout(0.5)

        # список клиентов, очередь сообщений
        self.clients = []
        self.messages = []

        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()

        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)

        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                SL.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            read_list = []
            send_list = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    read_list, send_list, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if read_list:
                for client_with_message in read_list:
                    try:
                        self.process_client_message(get_message(client_with_message),
                                                    self.messages, client_with_message,
                                                    self.clients, names)
                    except Exception as ex:
                        SL.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера. '
                                f'({ex})')
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            for mes in self.messages:
                try:
                    self.process_message(mes, names, send_list)
                except Exception:
                    SL.info(f'Связь с клиентом с именем {mes[DESTINATION]} была потеряна')
                    self.clients.remove(names[mes[DESTINATION]])
                    del names[mes[DESTINATION]]
            self.messages.clear()


main_server = Server()

if __name__ == '__main__':
    SL.debug("Запуск сервера произведён напрямую")
    main_server.general()
