import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logger = logging.getLogger(__name__)
level = logging.DEBUG
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(name)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения в Телегу."""
    logger.debug('Регестрируем с уровнем debug , если оно отправленно')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Успешная отправка сообщения.')
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')


def get_api_answer(current_timestamp):
    """запрос статуса домашней работы."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params=params)
    except Exception as error:
        raise SystemError(f'Ошибка получения request, {error}')
    else:
        if response.status_code == HTTPStatus.OK:
            logger.info('успешное получение Эндпоинта')
            homework = response.json()
            if 'error' in homework:
                raise SystemError(f'Ошибка json, {homework["error"]}')
            elif 'code' in homework:
                raise SystemError(f'Ошибка json, {homework["code"]}')
            else:
                return homework
        elif response.status_code == HTTPStatus.REQUEST_TIMEOUT:
            raise SystemError(f'Ошибка код {response.status_code}')
        elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise SystemError(f'Ошибка код {response.status_code}')
        else:
            raise SystemError(
                f'Недоступен Эндпоинт, код {response.status_code}')


def check_response(response):
    """проверка ответа на корректность."""
    try:
        homeworks = response['homeworks']
    except KeyError as key_error:
        msg = f'Нет ключа homeworks: {key_error}'
        logger.error(msg)
        raise exceptions.CheckResponseException(msg)
    if type(response) == dict:
        response['current_date']
        homeworks = response['homeworks']
    else:
        raise TypeError('Ответ от Домашки не словарь')
    if type(homeworks) == list:
        return homeworks
    else:
        raise TypeError('Тип ключа homeworks не list')


def parse_status(homework):
    """Парсинг информации о домашке."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise KeyError('В ответе API нет ключа homework_name')
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS.get(homework_status)
        return ('Изменился статус проверки '
                + f'работы "{homework_name}". {verdict}')
    else:
        raise SystemError('неизвестный статус')


def check_tokens():
    """Проверка доступности необходимых токенов."""
    token = all([
        PRACTICUM_TOKEN is not None,
        TELEGRAM_TOKEN is not None,
        TELEGRAM_CHAT_ID is not None
    ])
    if not token:
        logger.critical('Ошибка импорта токенов Telegramm.')
    else:
        return True


def main():
    """Бот для отслеживания статуса домашки на Яндекс.Домашка."""
    if check_tokens():
        logging.info('Токены впорядке')
    else:
        logging.critical(
            'Не обнаружен один из ключей PRACTICUM_TOKEN,'
            'TELEGRAM_TOKEN, TELEGRAM_CHAT_ID'
        )
    if not check_tokens():
        raise SystemExit('Я вышел')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Сообщение Telegram было отправлено')
    current_timestamp = int(time.time())
    logger.info('Бот запущен')
    while True:
        try:
            if type(current_timestamp) is not int:
                raise SystemError('В функцию передана не дата')
            response = get_api_answer(current_timestamp)
            response = check_response(response)
            if len(response) > 0:
                homework_status = parse_status(response[0])
                if homework_status is not None:
                    send_message(bot, homework_status)
            else:
                logger.debug('нет новых статусов')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message, exc_info=True)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)
            logging.info(message.format(message))


if __name__ == '__main__':
    main()
