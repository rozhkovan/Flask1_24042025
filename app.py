from flask import Flask, request, jsonify
from random import choice
from typing import Any
from http import HTTPStatus

app = Flask(__name__)
app.json.ensure_ascii = False

about_me = {
    "name": "Андрей",
    "sufname": "Рожков",
    "email": "arozhkov@list.ru"
}

QUOTES_KEY = set(('author', 'text', 'rate'))
RATE_RANGE = range(1,6)

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
       "rate": 2,
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
       "rate": 4,
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
       "rate": 5,
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так.",
       "rate": 2,
   },
]


def get_new_id() -> int:
    return quotes[-1].get('id') + 1


def get_index_by_id(id: int) -> int:
    for i in range(len(quotes)):
        if quotes[i].get('id') == id:
            return i
    return None


@app.route("/")
def hello_world() -> dict:
    return jsonify(data = "Hello, World!"), HTTPStatus.OK


@app.route("/about")
def about() -> dict:
    return jsonify(about_me), HTTPStatus.OK


@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]: 
    return jsonify(quotes), HTTPStatus.OK


@app.route("/quotes", methods=['POST'])
def create_quote() -> dict:
    new_data = dict(request.json)
    wrong_keys = set(new_data.keys()) - QUOTES_KEY
    if wrong_keys:
        return jsonify(error = f"Недопустимый ключ {wrong_keys}"), HTTPStatus.BAD_REQUEST
    new_data['id'] = get_new_id()
    new_rate = new_data.get('rate')
    if new_rate is None or new_rate not in RATE_RANGE:
        # if new_rate not in RATE_RANGE:
        new_data['rate'] = min(RATE_RANGE)
    # else:
    #     new_data['rate'] = 1 
    quotes.append(new_data)
    return jsonify(new_data), HTTPStatus.OK


@app.route("/quotes/<int:id>")
def get_quote(id : int) -> dict:
    index = get_index_by_id(id) 
    if index:
        return jsonify(quotes[index]), HTTPStatus.OK
    return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id: int) -> dict:
    index = get_index_by_id(id)
    if index:
        new_data = dict(request.json)
        wrong_keys = set(new_data.keys()) - QUOTES_KEY
        if wrong_keys:
            return jsonify(error = f"Недопустимый ключ {wrong_keys}"), HTTPStatus.BAD_REQUEST
        new_rate = new_data.get('rate')
        if new_rate not in RATE_RANGE:
            new_data.pop['rate']
        quotes[index].update(new_data)
        # for key in new_data:
        #     quotes[index][key] = new_data[key]
        return jsonify(quotes[index]), HTTPStatus.OK
    return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id: int):
    index = get_index_by_id(id)
    if index:
        quotes.pop(index)
        return jsonify(message = f"Quote with id={id} is deleted."), HTTPStatus.OK
    return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/count")
def quotes_count():
    return jsonify(count = len(quotes)), HTTPStatus.OK


@app.route("/quotes/random")
def random_quote() -> dict:
    return jsonify(choice(quotes)) ,HTTPStatus.OK


@app.route("/quotes/filter", methods=['GET'])
def filtered_quotes() -> list[dict]:
    args = request.args.to_dict()
    rate_filter = args.get('rate')
    if rate_filter:
        args['rate'] = int(rate_filter)
    result = quotes.copy()
    for key in args:
        result = list(filter(lambda x: x[key] == args[key], result))
    return jsonify(result), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)
