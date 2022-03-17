import json
import logging
import os

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}
product = 'слона'
marker = False
DECIDED = [
    'ладно',
    'куплю',
    'покупаю',
    'хорошо',
    'я покупаю',
    'я куплю'
]

UNSURE_DECISION = [
    "Не хочу.",
    "Не буду.",
    "Отстань!",
]


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


@app.route('/')
def root():
    return 'привет привет'


def handle_dialog(req, res):
    global marker, product
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': UNSURE_DECISION
        }
        res['response']['text'] = f'Привет! Купи {product}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in DECIDED:
        res['response']['text'] = f'{product.capitalize()}' \
                                  f' можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = False

        marker = True
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {product}!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {
            'title': suggest,
            'hide': True
        }
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append(
            {
                "title": "Ладно",
                "url": f"https://market.yandex.ru/search?text={product[:-1]}",
                "hide": True
            }
        )

    return suggests


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
