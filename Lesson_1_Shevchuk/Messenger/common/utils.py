"""Вынесенные функции (утилиты)"""

import json
from .variables import MAX_PACKAGE_LENGTH, ENCODING
from dec import Log
from errors import IncorrectDataRecivedError, NonDictInputError


@Log()
def get_message(client):
    '''
    Утилита приёма и декодирования сообщения
    принимает байты выдаёт словарь,
    если принято что-то другое отдаёт
    ошибку значения.
    :param client: конечный клиент, от которого получено сообщение,
    :return:
    '''
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@Log()
def send_message(sock, message):
    '''
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его.
    :param sock: соккет,
    :param message: сообщение,
    :return:
    '''
    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
