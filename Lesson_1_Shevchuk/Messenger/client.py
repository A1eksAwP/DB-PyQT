"""Программа-клиент"""

# import sys
# import json
# import socket
# import time
# import logging
# import argparse
# import threading
# from logs.config import client_log_config
# from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
# from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
#     RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SEND, SENDER, TEXT, \
#     DESTINATION, EXIT, MIN_AVAILABLE_PORT, MAX_AVAILABLE_PORT
# # from common.utils import get_message, send_message
# from common.utils import *
# from dec import Log
# from metaclasses import ClientVerifier
# from descriptors import PortVerifier

import sys
import json
import socket
import time
import dis
import argparse
import logging
import threading
import logs.config.client_log_config
from common.variables import *
from common.utils import *
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from dec import Log
from metaclasses import ClientVerifier
from descriptors import PortVerifier

# Инициализация клиентского логера
CL = logging.getLogger('client')


@Log()
def argument_parse():
    # CL.info(f"Функция argument_parse активна")
    my_args = argparse.ArgumentParser()
    my_args.add_argument('a', default=DEFAULT_IP_ADDRESS, nargs='?')
    my_args.add_argument('p', default=DEFAULT_PORT, type=int, nargs='?')
    my_args.add_argument('-n', '--name', default=None, nargs='?')
    namespace = my_args.parse_args(sys.argv[1:])
    server_address = namespace.a
    server_port = namespace.p
    client_name = namespace.name

    # if not MIN_AVAILABLE_PORT <= server_port <= MAX_AVAILABLE_PORT:
    #     sys.exit(1)

    return server_address, server_port, client_name


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    name = "ClientSender"
    port = PortVerifier()

    def __init__(self, account_name, sock, server_address, server_port):
        self.account_name = account_name
        self.sock = sock
        self.address = server_address
        self.port = server_port
        super().__init__()

    @Log()
    def create_message(self):
        to_user = input('Введи имя получателя: ')
        message = input('Введи сообщение или "exit": ')

        generate_message = {
            ACTION: SEND,
            SENDER: self.account_name,
            TIME: time.time(),
            DESTINATION: to_user,
            TEXT: message
        }

        try:
            send_message(self.sock, generate_message)
            CL.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception as ex:
            CL.critical(f'Потеряно соединение с сервером. {ex}')
            sys.exit(1)
        # CL.info(f'Пользователем {account_name} сгенерировано сообщение для отправки: {generate_message}')s

    @Log()
    def run(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                CL.info('Завершение работы по команде пользователя.')
                # Задержка необходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')

    @staticmethod
    def print_help():
        """Функция выводящая справку по использованию команд"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @Log()
    def create_exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    name = "ClientReader"

    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    @Log()
    def run(self):
        # Функция - обработчик сообщений других пользователей, поступающих с сервера
        # CL.info(f"Функция run активна")
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message \
                        and message[ACTION] == SEND \
                        and SENDER in message \
                        and DESTINATION in message \
                        and TEXT in message \
                        and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[TEXT]}')
                    CL.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[TEXT]}')
                else:
                    CL.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                CL.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CL.critical(f'Потеряно соединение с сервером.')
                break


@Log()
def create_presence(account_name):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name: имя пользователя,
    :return:
    '''
    # CL.info(f"Функция create_presence активна для пользователя {account_name}")
    pattern = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    # CL.info(f"Для пользователя {account_name} было сформировано сообщение: {PRESENCE}")
    return pattern


@Log()
def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message: сообщение,
    :return:
    '''
    # CL.info(f"Функция process_ans активна с переданным сообщением: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : SERVER OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log()
def main():
    CL.debug("Запуск клиента произведён напрямую")
    server_address, server_port, client_name = argument_parse()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    CL.info(
        f'Запущен клиент со следующими параметрами: '
        f'адрес сервера: {server_address}, '
        f'порт: {server_port}, '
        f'имя клиента: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        swap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        swap.connect((server_address, server_port))
        send_message(swap, create_presence(client_name))
        answer = process_ans(get_message(swap))
        CL.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        # CL.error(f'Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ServerError as error:
        # CL.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        # CL.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        # CL.critical(
        #     f'Не удалось подключиться к серверу {server_address}:{server_port}, '
        #     f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    # else:
        # CL.info('Режим - отправка.') if client_mode == SEND_MODE else CL.info('Режим - приём сообщений.')
    else:
        # Если соединение с сервером установлено корректно,
        # запускаем клиентский процесс приёма сообщений
        client_reciever = ClientReader(client_name, swap)
        client_reciever.daemon = True
        client_reciever.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        client_sender = ClientSender(client_name, swap, server_address, server_port)
        client_sender.daemon = True
        client_sender.start()

        CL.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение, или пользователь
        # ввёл exit. Поскольку все события обрабатываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if client_reciever.is_alive() and client_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
