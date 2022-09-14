"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес
сетевого узла должен создаваться с помощью функции ip_address().
"""

import platform
import subprocess
import threading
from ipaddress import ip_address
from pprint import pprint


THREAD_LOCK = threading.Lock()
RES = {'Доступные узлы': "", "Недоступные узлы": ""}


def host_ping(hosts_list, many=False):
    print(f'Запуск проверки на доступность хостов: {hosts_list}')
    threads_list = []
    for host in hosts_list:
        try:
            host_ip = check_ip(host)
        except Exception as ex:
            print(f'{host} - {ex} воспринимаю как доменное имя')
            host_ip = host

        thread = threading.Thread(
            target=ping,
            args=(host_ip, RES, many),
            daemon=True
        )
        thread.start()
        threads_list.append(thread)

    for thread in threads_list:
        thread.join()

    if many:
        return RES


def check_ip(user_ip):
    try:
        ipv4 = ip_address(user_ip)
    except ValueError:
        raise Exception('Некорректный ip адрес')
    return ipv4


def ping(ipv4, result, many):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    response = subprocess.Popen(["ping", param, '1', '-w', '1', str(ipv4)],
                                stdout=subprocess.PIPE)
    if response.wait() == 0:
        with THREAD_LOCK:
            result["Доступные узлы"] += f"{ipv4}\n"
            res = f"{ipv4} - Узел доступен"
            if not many:  # если результаты не надо добавлять в словарь, значит отображаем
                print(res)
            return res
    else:
        with THREAD_LOCK:
            result["Недоступные узлы"] += f"{ipv4}\n"
            res = f"{str(ipv4)} - Узел недоступен"
            if not many:  # если результаты не надо добавлять в словарь, значит отображаем
                print(res)
            return res


if __name__ == '__main__':
    # список проверяемых хостов
    hosts_list = ['192.168.0.1', '8.8.8.8', 'yandex.ru', 'google.com',
                  'gb.ru', 'youtube.com', '192.168.0.200', '192.168.1.1', '192.168.15.10',
                  '192.168.2.2', '0.0.0.1', '8.8.0.8', '8.8.4.4', '1.0.1.0']
    host_ping(hosts_list)
    pprint(RES)
