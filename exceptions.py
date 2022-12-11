class InvalidHttpStatus(Exception):
    """Статут ответа от API Яндекс.Практикума отличный от 200."""
    pass


class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашнего задания."""
    pass


class KeyHomeworkStatusIsInaccessible(Exception):
    """В ответе API Яндекс.Практикума в словаре 'homeworks'.
    отсутствует ключ 'status'.
    """
    pass


class ServiceError(Exception):
    """Ошибка отсутствия доступа по заданному эндпойнту."""
    pass


class NetworkError(Exception):
    """Ошибка отсутствия сети."""
    pass


class EndpointError(Exception):
    """Ошибка, если эндпойнт не корректен."""
    pass


class MessageSendingError(Exception):
    """Ошибка отправки сообщения."""
    pass


class GlobalsError(Exception):
    """Ошибка, если есть пустые глобальные переменные."""
    pass


class DataTypeError(Exception):
    """Ошибка, если тип данных не dict."""
    pass


class ResponseFormatError(Exception):
    """Ошибка, если формат response не json."""
    pass


class CheckResponseException (Exception):
    pass