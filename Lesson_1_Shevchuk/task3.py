"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок.
"""

# для формирования списка хостов и проверки доступности используем функцию из задания 2
from tabulate import tabulate
from task2 import host_range_ping


def host_range_ping_tab():

    RES = host_range_ping(True)  # Запрашиваем хосты, проверяем доступность, получаем словарь
    print(tabulate([RES], headers='keys', tablefmt='pipe', stralign='center'))


if __name__ == "__main__":
    host_range_ping_tab()
