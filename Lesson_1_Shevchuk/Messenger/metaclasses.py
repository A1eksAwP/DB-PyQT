"""Модуль метаклассов для сервера и клиента"""
import dis


# Метакласс для проверки соответствия сервера:
from pprint import pprint


class ServerVerifier(type):
    def __init__(cls, res_name, res_bases, res_dict):
        """
        res_name - экземпляр метакласса - Server
        res_bases - кортеж базовых классов - ()
        res_dict - словарь атрибутов и методов экземпляра метакласса
        """

        # Списки методов, используемые в функциях класса:
        method_list, attr_list = [], []

        # перебираем ключи
        for key in res_dict:
            # Пробуем
            try:
                dis_result = dis.get_instructions(res_dict[key])
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for instruction in dis_result:

                    if instruction.opname == 'LOAD_METHOD':
                        if instruction.argval not in method_list:
                            # заполняем список атрибутами, использующимися в функциях класса
                            method_list.append(instruction.argval)
                    elif instruction.opname == 'LOAD_ATTR':
                        if instruction.argval not in attr_list:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attr_list.append(instruction.argval)
        print(20*'-', 'method_list', 20*'-')
        pprint(method_list)
        print(20*'-', 'attr_list', 20*'-')
        pprint(attr_list)
        print(50*'-')
        # Если обнаружено использование недопустимого метода connect, вызываем исключение:
        if 'connect' in method_list:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        # Если сокет не инициализировался константами SOCK_STREAM(TCP) и AF_INET(IPv4), тоже исключение.
        if not ('SOCK_STREAM' in attr_list and 'AF_INET' in attr_list):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(res_name, res_bases, res_dict)


# Метакласс для проверки корректности клиентов:
class ClientVerifier(type):
    def __init__(cls, res_name, res_bases, res_dict):
        # Список методов, которые используются в функциях класса:
        pprint(res_dict)
        global_list, method_list, attr_list = [], [], []
        for key in res_dict:
            pprint('-' * 30)
            pprint(key)
            # Пробуем
            try:
                dis_result = dis.get_instructions(res_dict[key])
                # Если не функция, то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for instruction in dis_result:
                    print(instruction)
                    method_list.append(instruction.argval)
                    if instruction.opname == 'LOAD_GLOBAL':
                        if instruction.argval not in global_list:
                            global_list.append(instruction.argval)
                    elif instruction.opname == 'LOAD_METHOD':
                        if instruction.argval not in method_list:
                            # заполняем список атрибутами, использующимися в функциях класса
                            method_list.append(instruction.argval)
                    elif instruction.opname == 'LOAD_ATTR':
                        if instruction.argval not in attr_list:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attr_list.append(instruction.argval)
        print(20 * '-', 'global_list', 20 * '-')
        pprint(global_list)
        print(20 * '-', 'method_list', 20 * '-')
        pprint(method_list)
        print(20 * '-', 'attr_list', 20 * '-')
        pprint(attr_list)
        print(50 * '-')
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen', 'socket'):
            if command in method_list:
                raise TypeError('В классе обнаружено использование запрещённого метода')

        """
        Мне не удалось через модуль dis найти признаки TCP протокола в клиенте :(
        """

        # if 'connect' in method_list \
        #         or 'recv' in method_list \
        #         or 'send' in method_list \
        #         or 'close' in method_list:
        #     pass
        # else:
        #     raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')

        super().__init__(res_name, res_bases, res_dict)
