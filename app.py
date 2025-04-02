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
from sqlalchemy import String, UniqueConstraint, func, ForeignKey

from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass


QUOTES_KEYS = set(('author_id', 'text', 'rating'))
TABLE_FIELDS = ('id', 'author', 'text', 'rating')
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


class AuthorModel(Base): # db.Model):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32)) #, index= True, unique=True)
    surname: Mapped[str] = mapped_column(String(32), server_default='')
    quotes: Mapped[list['QuoteModel']] = relationship(back_populates='author', lazy='dynamic', cascade="all,delete-orphan")
    deleted: Mapped[bool] = mapped_column(default=False, server_default='false')
    
    __table_args__ = (UniqueConstraint('name', 'surname', name='AuthorFullNameConstrant'), )
    
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname
            }


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(nullable=False, default=1, server_default='1')
    deleted: Mapped[bool] = mapped_column(default=False, server_default='false')

    def __init__(self, author, text, rating):
        self.author = author
        self.text = text
        if rating in RATE_RANGE:
            self.rating = rating
        else:
            self.rating = 1

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "author": self.author.to_dict(),
            "text": self.text,
            "rating": self.rating
        }

    def to_dict_short(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "text": self.text,
            "rating": self.rating
        }

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(message = e.description), e.code


@app.route("/authors/<int:author_id>")
def get_author(author_id): 
    """Возвращает автора по id"""
    author = db.session.get(AuthorModel, author_id)
    if author and not author.deleted:
        return jsonify(author = author.to_dict()), HTTPStatus.OK
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors")
def get_authors() -> list[dict[str, Any]]: 
    """Возвращает список авторов"""
    authors_db = db.session.execute(db.select(AuthorModel).filter_by(deleted=False)).scalars()
    authors = []
    for author_db in authors_db:
        authors.append(author_db.to_dict())        
    return jsonify(authors), HTTPStatus.OK


@app.route("/authors/deleted")
def get_deleted_authors() -> list[dict[str, Any]]: 
    """Возвращает список удаленных авторов"""
    authors_db = db.session.execute(db.select(AuthorModel).filter_by(deleted=True)).scalars()
    authors = []
    for author_db in authors_db:
        authors.append(author_db.to_dict())        
    return jsonify(authors), HTTPStatus.OK


@app.route("/authors/name")
def get_name_ordered_authors() -> list[dict[str, Any]]: 
    """Возвращает список авторов в сортировке по имени"""
    authors_db = db.session.execute(db.select(AuthorModel).filter_by(deleted=False).order_by(AuthorModel.name)).scalars()
    authors = []
    for author_db in authors_db:
        authors.append(author_db.to_dict())        
    return jsonify(authors), HTTPStatus.OK


@app.route("/authors/surname")
def get_surname_ordered_authors() -> list[dict[str, Any]]: 
    """Возвращает список авторов в сортировке по имени"""
    authors_db = db.session.execute(db.select(AuthorModel).filter_by(deteted=False).order_by(AuthorModel.surname)).scalars()
    authors = []
    for author_db in authors_db:
        authors.append(author_db.to_dict())        
    return jsonify(authors), HTTPStatus.OK


@app.route("/authors", methods=["POST"])
def create_author():
    """Создает нового автора"""
    author_data = request.json
    name = author_data.get('name')
    surname = author_data.get('surname')
    if name:
        if not surname:
            surname = ""
        author = AuthorModel(name, surname)
        db.session.add(author)
        db.session.commit()
        return author.to_dict(), HTTPStatus.CREATED
    return jsonify(message = f'Incomplete data {author_data}'), HTTPStatus.BAD_REQUEST


@app.route("/authors/<int:author_id>", methods=["PUT"])
def edit_author(author_id):
    """Редактирует автора по id"""
    author_data = request.json
    author = db.session.get(AuthorModel, author_id)
    if author:
        author_name = author_data.get('name')
        if author_name:
            author.name = author_name
        author_surname = author_data.get('surname')
        if author_surname:
            author.surname = author_surname
        db.session.commit()
        return author.to_dict(), HTTPStatus.OK
    return jsonify(message=f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


# @app.route("/authors/<int:author_id>", methods=["DELETE"])
# def delete_author(author_id):
#     """Удаляет автора по id"""
#     author = db.session.get(AuthorModel, author_id)
#     if author:
#         db.session.delete(author)
#         db.session.commit()
#         return jsonify(message = f"Author with id={author_id} deleted."), HTTPStatus.OK
#     return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    """Удаляет автора по id"""
    author = db.session.get(AuthorModel, author_id)
    if author and not author.deleted:
        author.deleted = True
        # db.session.commit()
        for quote in author.quotes:
            quote.deleted = True        
        db.session.commit()
        return jsonify(message = f"Author with id={author_id} deleted."), HTTPStatus.OK
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors/restore/<int:author_id>", methods=["PUT"])
def restore_author(author_id):
    """Восстанавливает удаленного автора по id"""
    author = db.session.get(AuthorModel, author_id)
    if author and author.deleted:
        author.deleted = False
        for quote in author.quotes:
            quote.deleted = False        
        db.session.commit()
        return jsonify(message = f"Author with id={author_id} restored."), HTTPStatus.OK
    return jsonify(message = f"Deleted author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors/<int:author_id>/quotes")
def get_author_quotes(author_id):
    """Выводит список цитат по id автора""" 
    author = db.session.get(AuthorModel, author_id)
    if author and not author.deleted:
        quotes = []
        for quote_db in author.quotes:
            quotes.append(quote_db.to_dict_short())        
        return jsonify(author = author.to_dict(), quotes = quotes), HTTPStatus.OK
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_author_quote(author_id: int):
    """Создает цитату для указанного id автора"""
    author = db.session.get(AuthorModel, author_id)
    if author and not author.deleted:
        new_data = request.json
        quote = QuoteModel(author, new_data["text"])
        new_rating = new_data.get('rating')
        if new_rating and new_rating in RATE_RANGE:
            quote.rating = new_rating
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict(), HTTPStatus.CREATED
    return jsonify(message = f"Author with id={author_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]:
    """Выводит список цитат""" 
    quotes_db = db.session.execute(db.select(QuoteModel).filter_by(deleted=False)).scalars()
    quotes = []
    for quote_db in quotes_db:
        author = db.session.get(AuthorModel ,quote_db.author_id)
        quotes.append(quote_db.to_dict())        
    return jsonify(quotes), HTTPStatus.OK


# @app.route("/quotes", methods=['POST'])
# def create_quote() -> dict:
#     # Проверка данных
#     new_data = dict(request.json)
#     wrong_keys = set(new_data.keys()) - QUOTES_KEYS
#     if wrong_keys:
#         return jsonify(message = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
#     new_rating = new_data.get('rating')
#     if new_rating is None or new_rating not in RATE_RANGE:
#         new_data['rating'] = min(RATE_RANGE)

#     # Вставка записи
#     # quote = QuoteModel(new_data['author'], new_data['text'], new_data['rating'])
#     quote_db = QuoteModel(new_data['author'], new_data['text'])
#     db.session.add(quote_db)
#     db.session.commit()
#     return jsonify(quote_db.to_dict()), HTTPStatus.OK


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id : int) -> dict:
    """Выводит цитату по id"""
    quote = db.session.get(QuoteModel, quote_id)
    if quote and not quote.deleted:
        return jsonify(quote.to_dict()), HTTPStatus.OK
    return jsonify(message = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id: int) -> dict:
    """Редактирует цитату по id"""
    # Проверка данных
    new_data = dict(request.json)
    wrong_keys = set(new_data.keys()) - QUOTES_KEYS
    if wrong_keys:
        return jsonify(message = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
    # new_rating = new_data.get('rating')
    # if new_rating and new_rating not in RATE_RANGE:
    #     new_data.pop['rating']

    # Обновление записи
    quote = db.session.get(QuoteModel, quote_id)
    if quote and not quote.deleted:
        new_author_id = new_data.get('author_id')
        if new_author_id:
            new_author = db.session.get(AuthorModel, new_author_id)
            if new_author:
                quote.author_id = new_author_id
            else:
                return jsonify(message = f"Author with id={new_author_id} not found"), HTTPStatus.BAD_REQUEST
        new_text = new_data.get('text')
        if new_text:
            quote.text = new_text
        new_rating = new_data.get('rating')
        if new_rating and new_rating in RATE_RANGE:
            quote.rating = new_rating

        # quote = quote_db.to_dict()
        # quote.update(new_data)
        # quote_db.author = quote['author']
        # quote_db.text = quote['text']
        db.session.commit()
        return jsonify(quote.to_dict()), HTTPStatus.OK
    return jsonify(message = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND

@app.route("/quotes/<int:quote_id>/up", methods=['PUT'])
def up_quote(quote_id: int) -> None:
    """Повышает рейтинг цитаты"""
    quote = db.session.get(QuoteModel, quote_id)
    if quote and not quote.deleted:
        new_rating = quote.rating + 1
        if new_rating in RATE_RANGE:
            quote.rating = new_rating
            db.session.commit()
            return jsonify(message = f"Your vote has been accepted, new rating is {new_rating}."), HTTPStatus.OK
        return jsonify(message=f"Quote with id={quote_id} has maximal rating."), HTTPStatus.OK
    return jsonify(message = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:quote_id>/down", methods=['PUT'])
def down_quote(quote_id: int) -> None:
    """Понижает рейтинг цитаты"""
    quote = db.session.get(QuoteModel, quote_id)
    if quote and not quote.deleted:
        new_rating = quote.rating - 1
        if new_rating in RATE_RANGE:
            quote.rating = new_rating
            db.session.commit()
            return jsonify(message = f"Your vote has been accepted, new rating is {new_rating}."), HTTPStatus.OK
        return jsonify(message=f"Quote with id={quote_id} has minimal rating."), HTTPStatus.OK
    return jsonify(message = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id: int):
    """Удаляет цитату по id"""
    # quote_db = db.session.execute(db.select(QuoteModel).filter_by(id=quote_id)).scalar_one_or_none()
    quote = db.session.get(QuoteModel, quote_id)
    if quote and not quote.deleted:
        db.session.delete(quote)
        db.session.commit()
        return jsonify(message = f"Quote with id={quote_id} deleted."), HTTPStatus.OK
    return jsonify(message = f"Quote with id={quote_id} not found"), HTTPStatus.NOT_FOUND


@app.route("/quotes/count")
def quotes_count():
    """Выводит количество цитат в базе данных"""
    # todo Странный метод
    # user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()
    quotes = db.session.execute(db.select(QuoteModel.id).filter_by(deleted=False)).scalars()
    if quotes:
        i = 0
        for quote in quotes:
            i += 1
        return jsonify(count = i), HTTPStatus.OK
    abort(503)
    
    # db.session.query()
    # count_quotes = "SELECT count(*) as Count FROM quotes"
    # cursor = get_db().cursor()
    # cursor.execute(count_quotes)
    # count = cursor.fetchone()
    # if count:
    #     return jsonify(count = count[0]), HTTPStatus.OK
    # abort(503)


@app.route("/quotes/random")
def random_quote() -> dict:
    """Выводит случайную цитату"""
    quotes_db = db.session.execute(db.select(QuoteModel).filter_by(deleted=False)).scalars()
    quotes = []
    for quote_db in quotes_db:
        quotes.append(quote_db.to_dict())        
    return jsonify(choice(quotes)), HTTPStatus.OK


@app.route("/quotes/filter", methods=['GET'])
def filtered_quotes() -> list[dict]:
    """Выводит отфильтрованный список цитат"""
    args = request.args.to_dict()

    # quotes = db.session.execute(db.select(QuoteModel).filter_by(id=id)).scalar_one_or_none()
    # if name_filter:
        # quotes_db = db.session.execute(db.select(QuoteModel).filter_by(QuoteModel.author.has(name=name_filter)).scalars()
        # query = db.select(QuoteModel).filter_by(**args)

    query = db.select(QuoteModel).filter_by(**args)
    quotes_db = db.session.execute(query).scalars()
    quotes = []
    for quote_db in quotes_db:
        if not quote_db.deleted:
            quotes.append(quote_db.to_dict())        
    return jsonify(quotes), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)
