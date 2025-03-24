from flask import Flask
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
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


@app.route("/quotes")
def quote():
    return quotes


@app.route("/quotes/<int:id>")
def quote_by_id(id):
    for q in quotes:
        if q.get('id') == id:
            return q
    return f"Quote with id={id} not found", 404


@app.route("/quotes/count")
def quotes_count():
    return dict(count=len(quotes))


@app.route("/quotes/random")
def random_quote():
    return random.choice(quotes)


if __name__ == "__main__":
    app.run(debug=True)
