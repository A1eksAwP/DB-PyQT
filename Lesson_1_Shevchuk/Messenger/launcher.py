"""Лаунчер"""

import subprocess
TERMINAL = []


def main():
    clients_count = int(input('Сколько клиентов инициализировать: '))
    while True:
        user_key = input('''
        Выберите действие: 
        q - выход,
        w - запустить сервер и клиент, 
        e - закрыть все окна: 
        ''')
        if user_key == 'q':
            break
        elif user_key == 'w':
            TERMINAL.append(subprocess.Popen(
                'python server.py',
                creationflags=subprocess.CREATE_NEW_CONSOLE)
            )
            for client in range(clients_count):
                TERMINAL.append(subprocess.Popen(
                    f'python client.py -n test{client}',
                    creationflags=subprocess.CREATE_NEW_CONSOLE))

        elif user_key == 'e':
            while TERMINAL:
                victim_process = TERMINAL.pop()
                victim_process.kill()


if __name__ == '__main__':
    main()