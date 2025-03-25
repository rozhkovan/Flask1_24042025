from flask import Flask, request
import random

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


def get_new_id():
    return quotes[-1].get('id') + 1


def get_index_by_id(id: int):
    for i in range(len(quotes)):
        if quotes[i].get('id') == id:
            return i
    return None


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


@app.route("/quotes")
def get_quote():
    return quotes


@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    q = dict(data)
    q['id'] = get_new_id()
    new_rate = q.get('rate')
    if new_rate:
        if new_rate < 1 or new_rate > 5:
            q['rate'] = 1
    else:
        q['rate'] = 1 
    quotes.append(q)
    return q, 200


@app.route("/quotes/<int:id>")
def quote_by_id(id):
    index = get_index_by_id(id) 
    if index:
        return quotes[index]
    return f"Quote with id={id} not found", 404


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    data = request.json
    index = get_index_by_id(id)
    if index: 
        new = dict(data)
        if new.get('author'):
            quotes[index]['author'] = new.get('author')
        if new.get('text'):
            quotes[index]['text'] = new.get('text')
        new_rate = new.get('rate')
        if new_rate < 1 or new_rate > 5:
            pass            
        else:
            quotes[index]['rate'] = new_rate
        return quotes[index], 200
    return {}, 404


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    index = get_index_by_id(id)
    if index:
        quotes.pop(index)
        return f"Quote with id {id} is deleted.", 200
    return {}, 404


@app.route("/quotes/count")
def quotes_count():
    return dict(count=len(quotes))


@app.route("/quotes/random")
def random_quote():
    return random.choice(quotes)


@app.route("/quotes/filter", methods=['GET'])
def filtered_quotes():
    args = request.args.to_dict()
    autor_filter = args.get('author')
    rate_filter = args.get('rate')
    text_filter = args.get('text')
    result = quotes
    if autor_filter:
        result = list(filter(lambda x: x['author'] == autor_filter, result))
    if rate_filter:
        result = list(filter(lambda x: x['rate'] == int(rate_filter), result))
    if text_filter:
        result = list(filter(lambda x: x['text'] == text_filter, result))
    return result


if __name__ == "__main__":
    app.run(debug=True)
