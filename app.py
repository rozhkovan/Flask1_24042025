from flask import Flask, request, jsonify
from random import choice
from typing import Any

app = Flask(__name__)
app.json.ensure_ascii = False

about_me = {
    "name": "Андрей",
    "sufname": "Рожков",
    "email": "arozhkov@list.ru"
}

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
    return jsonify(data = "Hello, World!")


@app.route("/about")
def about() -> dict:
    return jsonify(about_me)


@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]: 
    return jsonify(quotes)


@app.route("/quotes", methods=['POST'])
def create_quote() -> dict:
    q = dict(request.json)
    q['id'] = get_new_id()
    new_rate = q.get('rate')
    if new_rate:
        if new_rate not in range(1,6):
            q['rate'] = 1
    else:
        q['rate'] = 1 
    quotes.append(q)
    return jsonify(q), 200


@app.route("/quotes/<int:id>")
def get_quote(id : int) -> dict:
    index = get_index_by_id(id) 
    if index:
        return jsonify(quotes[index])
    return jsonify(error = f"Quote with id={id} not found"), 404


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id: int) -> dict:
    index = get_index_by_id(id)
    if index:
        new = dict(request.json)
        new_rate = new.get('rate')
        if new_rate not in range(1,6):
            new['rate'] = quotes[index]['rate']
        for key in new:
            quotes[index][key] = new[key]
        return jsonify(quotes[index]), 200
    return jsonify(error = f"Quote with id={id} not found"), 404


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id: int):
    index = get_index_by_id(id)
    if index:
        quotes.pop(index)
        return jsonify(message = f"Quote with id={id} is deleted."), 200
    return jsonify(error = f"Quote with id={id} not found"), 404


@app.route("/quotes/count")
def quotes_count():
    return jsonify(count = len(quotes))


@app.route("/quotes/random")
def random_quote() -> dict:
    return jsonify(choice(quotes))


@app.route("/quotes/filter", methods=['GET'])
def filtered_quotes() -> list[dict]:
    args = request.args.to_dict()
    rate_filter = args.get('rate')
    if rate_filter:
        args['rate'] = int(rate_filter)
    result = quotes
    for key in args:
        result = list(filter(lambda x: x[key] == args[key], result))
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
