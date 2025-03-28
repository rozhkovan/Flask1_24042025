from flask import Flask, request, jsonify, g, abort
from werkzeug.exceptions import HTTPException
from random import choice
from typing import Any
from http import HTTPStatus
from pathlib import Path
# import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func, ForeignKey

from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass


QUOTES_KEYS = set(('author', 'text', 'rate'))
TABLE_FIELDS = ('id', 'author', 'text', 'rate')
RATE_RANGE = range(1,6)

BASE_DIR = Path(__file__).parent
# path_to_db = BASE_DIR / "store.db"

app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(32), index= True, unique=True)
    quotes: Mapped[list['QuoteModel']] = relationship(back_populates='author', lazy='dynamic', cascade="all,delete-orphan")
    
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
            }


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text):
        self.author = author
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            # "author": self.author,
            "text": self.text
        }


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(message = e.description), e.code


@app.route("/authors/<int:author_id>")
def get_author(author_id): 
    author = db.session.get(AuthorModel, author_id)
    if author:
        return jsonify(author = author.to_dict()), HTTPStatus.OK
    return jsonify(error = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors")
def get_authors() -> list[dict[str, Any]]: 
    authors_db = db.session.execute(db.select(AuthorModel)).scalars()
    authors = []
    for author_db in authors_db:
        authors.append(author_db.to_dict())        
    return jsonify(authors), HTTPStatus.OK


@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), HTTPStatus.CREATED


# @app.route("/authors/<int:author_id>", methods=["PUT"])
# def edit_author(author_id):
#     author_data = request.json
#     author = db.session.get(AuthorModel, author_id)
#     # author = AuthorModel(author_data["name"])

#     print(**author_data)
#     # db.session.add(author)
#     # db.session.commit()
#     return author.to_dict(), HTTPStatus.CREATED


@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    author = db.session.get(AuthorModel, author_id)
    if author:
        db.session.delete(author)
        db.session.commit()
        return jsonify(message = f"Author with id={author_id} deleted."), HTTPStatus.OK
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors/<int:author_id>/quotes")
def get_author_quotes(author_id): 
    author = db.session.get(AuthorModel, author_id)
    quotes = []
    for quote_db in author.quotes:
        quotes.append(quote_db.to_dict())        
    return jsonify(author = author.to_dict(), quotes = quotes), HTTPStatus.OK


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_author_quote(author_id: int):
    author = db.session.get(AuthorModel, author_id)
    if author:
        new_data = request.json
        quote = QuoteModel(author, new_data["text"])
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict(), HTTPStatus.CREATED
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]: 
    quotes_db = db.session.execute(db.select(QuoteModel)).scalars()
    quotes = []
    for quote_db in quotes_db:
        quotes.append(quote_db.to_dict())        
    return jsonify(quotes), HTTPStatus.OK


# @app.route("/quotes", methods=['POST'])
# def create_quote() -> dict:
#     # Проверка данных
#     new_data = dict(request.json)
#     wrong_keys = set(new_data.keys()) - QUOTES_KEYS
#     if wrong_keys:
#         return jsonify(error = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
#     new_rate = new_data.get('rate')
#     if new_rate is None or new_rate not in RATE_RANGE:
#         new_data['rate'] = min(RATE_RANGE)

#     # Вставка записи
#     # quote = QuoteModel(new_data['author'], new_data['text'], new_data['rate'])
#     quote_db = QuoteModel(new_data['author'], new_data['text'])
#     db.session.add(quote_db)
#     db.session.commit()
#     return jsonify(quote_db.to_dict()), HTTPStatus.OK


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id : int) -> dict:
    # quote_db = db.session.execute(db.select(QuoteModel).filter_by(id=id)).scalar_one_or_none()
    quote = db.session.get(QuoteModel, quote_id)
    if quote:
        # quote = qoute_db.to_dict()
        return jsonify(quote.to_dict()), HTTPStatus.OK
    return jsonify(error = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


# @app.route("/quotes/<int:quote_id>", methods=['PUT'])
# def edit_quote(quote_id: int) -> dict:
#     # Проверка данных
#     new_data = dict(request.json)
#     wrong_keys = set(new_data.keys()) - QUOTES_KEYS
#     if wrong_keys:
#         return jsonify(error = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
#     new_rate = new_data.get('rate')
#     if new_rate and new_rate not in RATE_RANGE:
#         new_data.pop['rate']

#     # Обновление записи
#     quote_db = db.session.execute(db.select(QuoteModel).filter_by(id=quote_id)).scalar_one_or_none()
#     if quote_db:
#         quote = quote_db.to_dict()
#         quote.update(new_data)
#         quote_db.author = quote['author']
#         quote_db.text = quote['text']
#         db.session.commit()
#         return jsonify(quote_db.to_dict()), HTTPStatus.OK
#     return jsonify(error = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id: int):
    # quote_db = db.session.execute(db.select(QuoteModel).filter_by(id=quote_id)).scalar_one_or_none()
    quote = db.session.get(QuoteModel, quote_id)
    if quote:
        db.session.delete(quote)
        db.session.commit()
        return jsonify(message = f"Quote with id={quote_id} deleted."), HTTPStatus.OK
    return jsonify(error = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


# @app.route("/quotes/count")
# def quotes_count():
#     count_quotes = "SELECT count(*) as Count FROM quotes"
#     cursor = get_db().cursor()
#     cursor.execute(count_quotes)
#     count = cursor.fetchone()
#     if count:
#         return jsonify(count = count[0]), HTTPStatus.OK
#     abort(503)


@app.route("/quotes/random")
def random_quote() -> dict:
    quotes_db = db.session.execute(db.select(QuoteModel)).scalars()
    quotes = []
    for quote_db in quotes_db:
        quotes.append(quote_db.to_dict())        
    return jsonify(choice(quotes)), HTTPStatus.OK


# @app.route("/quotes/filter", methods=['GET'])
# def filtered_quotes() -> list[dict]:
#     args = request.args.to_dict()
#     rate_filter = args.get('rate')
#     if rate_filter:
#         args['rate'] = int(rate_filter)

#     select_quotes = "SELECT * FROM quotes"
#     cursor = get_db().cursor()
#     cursor.execute(select_quotes)
#     quotes_db = cursor.fetchall()
#     # keys = ('id', 'author', 'text', 'rate')
#     quotes = []
#     for quote_db in quotes_db:
#         quote = dict(zip(TABLE_FIELDS, quote_db))
#         quotes.append(quote)

#     result = quotes.copy()
#     for key in args:
#         result = list(filter(lambda x: x[key] == args[key], result))
#     return jsonify(result), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)
