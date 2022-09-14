"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from task1 import check_ip, host_ping
import re

MAX_OCTET = 255


def host_range_ping(many=False):
  
    while True:
        user_start_ip = input("Введите первоначальный адрес: ")
        try:
            ipv4_start = check_ip(user_start_ip)
            # last_oct = int(start_ip.split('.')[-1])       # смотрим чему равен последний октет
            last_oct = int(re.findall(r'\d+$', user_start_ip)[0])
            break
        except Exception as ex:
            print(ex)
    while True:
        user_end_ip = input(f"Сколько адресов от {user_start_ip} хотите проверить?: ")  # Запрос на количество проверяемых адресов
        if not user_end_ip.isnumeric():
            print("Необходимо ввести число")
        else:
            if (last_oct + int(user_end_ip)) > MAX_OCTET:  # По условию меняется только последний октет
                print(f"Можем менять только последний октет, "
                      f"т.е. максимальное число хостов {MAX_OCTET - last_oct}")
            else:
                break
    host_list = []
    [host_list.append(str(ipv4_start + x)) for x in range(int(user_end_ip))]  # формируем список всех ip

    return host_ping(host_list) if not many else host_ping(host_list, True)


if __name__ == "__main__":
    host_range_ping()
