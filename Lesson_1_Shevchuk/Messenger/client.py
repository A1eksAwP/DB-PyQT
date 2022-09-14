"""Программа-клиент"""

import sys
import json
import socket
import time
import logging
import argparse
import threading
from logs.config import client_log_config
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SEND, SENDER, TEXT, \
    ACCEPT_MODE, SEND_MODE, DESTINATION, EXIT
from common.utils import get_message, send_message
from dec import Log


# Инициализация клиентского логера
CL = logging.getLogger('client')
MODES = (ACCEPT_MODE, SEND_MODE)


class Client:
    name = "Client"

    def __init__(self):
        pass

    @Log()
    def create_message(self, sock, account_name='Guest/Default'):
        to_user = input('Введи имя получателя: ')
        message = input('Введи сообщение или "exit": ')

        generate_message = {
            ACTION: SEND,
            SENDER: account_name,
            TIME: time.time(),
            DESTINATION: to_user,
            TEXT: message
        }

        try:
            send_message(sock, generate_message)
            CL.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            CL.critical('Потеряно соединение с сервером.')
            sys.exit(1)
        # CL.info(f'Пользователем {account_name} сгенерировано сообщение для отправки: {generate_message}')
        return generate_message

    @Log()
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                send_message(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                CL.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @staticmethod
    def print_help():
        """Функция выводящая справку по использованию команд"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @staticmethod
    @Log()
    def create_presence(account_name='Guest/Default'):
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

    @staticmethod
    @Log()
    def create_exit_message(account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @staticmethod
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

    @staticmethod
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

        if not 1023 < server_port < 65536:
            # CL.critical(
            #     f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            #     f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)

        return server_address, server_port, client_name

    @staticmethod
    @Log()
    def message_from_server(socket, username):
        # Функция - обработчик сообщений других пользователей, поступающих с сервера
        # CL.info(f"Функция message_from_server активна")
        while True:
            try:
                message = get_message(socket)
                if ACTION in message \
                        and message[ACTION] == SEND \
                        and SENDER in message \
                        and DESTINATION in message \
                        and TEXT in message \
                        and message[DESTINATION] == username:
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
    def general(self):
        # CL.info(f"Функция general активна")
        server_address, server_port, client_name = self.argument_parse()

        CL.info(
            f'Запущен клиент со следующими параметрами: '
            f'адрес сервера: {server_address}, '
            f'порт: {server_port}, '
            f'имя клиента: {client_name}')

        # Инициализация сокета и сообщение серверу о нашем появлении

        try:
            swap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            swap.connect((server_address, server_port))
            send_message(swap, self.create_presence(client_name))
            answer = self.process_ans(message=get_message(swap))
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
            client_process = threading.Thread(target=self.message_from_server, args=(swap, client_name))
            client_process.daemon = True
            client_process.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            active_process = threading.Thread(target=self.user_interactive, args=(swap, client_name))
            active_process.daemon = True
            active_process.start()
            CL.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение, или пользователь
            # ввёл exit. Поскольку все события обрабатываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if client_process.is_alive() and active_process.is_alive():
                    continue
                break


default_client = Client()
CL.info(f"Создан экземпляр класса Client")

if __name__ == '__main__':
    CL.debug("Запуск клиента произведён напрямую")
    default_client.general()
