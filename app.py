from flask import Flask, request, jsonify, g
from random import choice
from typing import Any
from http import HTTPStatus
from pathlib import Path
import sqlite3


QUOTES_KEYS = set(('author', 'text', 'rate'))
RATE_RANGE = range(1,6)

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db"

app = Flask(__name__)
app.json.ensure_ascii = False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]: 

    select_quotes = "SELECT * FROM quotes"

    # connection = sqlite3.connect(path_to_db)
    # cursor = connection.cursor()
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall() # get list[tuple]
    # print(f"{quotes=}")
    cursor.close()
    # connection.close()
    # Подготовка данных для отправки в правильном формате
    # Необходимо выполнить преобразование:
    # list[tuple] -> list[dict]
    keys = ('id', 'author', 'text')
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)
        
    return jsonify(quotes), HTTPStatus.OK


@app.route("/quotes", methods=['POST'])
def create_quote() -> dict:
    insert_quote = "INSERT INTO quotes (author, text) VALUES(?, ?)"
    select_quote = "SELECT * FROM quotes WHERE id=?"

    # Проверка данных
    new_data = dict(request.json)
    wrong_keys = set(new_data.keys()) - QUOTES_KEYS
    if wrong_keys:
        return jsonify(error = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
    new_rate = new_data.get('rate')
    if new_rate is None or new_rate not in RATE_RANGE:
        new_data['rate'] = min(RATE_RANGE)

    # Вставка записи
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(insert_quote,(new_data['author'], new_data['text']))
    rec_id = cursor.lastrowid
    cursor.close()
    connection.commit()
    if not rec_id:
        connection.close()
        return jsonify(error="Insertion error"), HTTPStatus.BAD_REQUEST

    # Считывание вставленной записи
    cursor = connection.cursor()
    cursor.execute(select_quote,(rec_id,))
    quote_db = cursor.fetchone()
    cursor.close()
    connection.close()
    if not quote_db:
        return jsonify(error = f"Quote with id={rec_id} not found"), HTTPStatus.NOT_FOUND
    keys = ('id', 'author', 'text')
    quote = dict(zip(keys, quote_db))
    return jsonify(quote), HTTPStatus.OK


@app.route("/quotes/<int:id>")
def get_quote(id : int) -> dict:
    select_quote = "SELECT * FROM quotes WHERE id=?"

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(select_quote,(id,))
    quote_db = cursor.fetchone()
    cursor.close()
    connection.close()
    if not quote_db:
        return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND
    keys = ('id', 'author', 'text')
    quote = dict(zip(keys, quote_db))
    return jsonify(quote), HTTPStatus.OK


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id: int) -> dict:
    update_quote = "UPDATE quotes SET author=?, text=? WHERE id=?"
    select_quote = "SELECT * FROM quotes WHERE id=?"

    # Проверка данных
    new_data = dict(request.json)
    wrong_keys = set(new_data.keys()) - QUOTES_KEYS
    if wrong_keys:
        return jsonify(error = f"Wrong keys {wrong_keys}"), HTTPStatus.BAD_REQUEST
    new_rate = new_data.get('rate')
    if new_rate not in RATE_RANGE:
        new_data.pop['rate']

    # Считывание исходной записи
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(select_quote,(id,))
    quote_db = cursor.fetchone()
    cursor.close()
    if not quote_db:
        connection.close()
        return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND
    keys = ('id', 'author', 'text')
    quote = dict(zip(keys, quote_db))

    # Модификация записи
    quote.update(new_data)
    cursor = connection.cursor()
    cursor.execute(update_quote,(quote['author'], quote['text'], id))
    rows_updated = cursor.rowcount
    cursor.close()
    connection.commit()
    if not rows_updated:
        connection.close()
        return jsonify(error=f"Update error with id={id}"), HTTPStatus.BAD_REQUEST
    
    # Считывание обновленной записи
    cursor = connection.cursor()
    cursor.execute(select_quote,(id,))
    quote_db = cursor.fetchone()
    cursor.close()
    if not quote_db:
        connection.close()
        return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND
    keys = ('id', 'author', 'text')
    quote = dict(zip(keys, quote_db))
    return jsonify(quote), HTTPStatus.OK


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id: int):
    delete_quote = "DELETE FROM quotes WHERE id=?"

    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(delete_quote,(id,))
    rows_deleted = cursor.rowcount
    cursor.close()
    connection.commit()
    connection.close()
    if rows_deleted:
        return jsonify(message = f"Quote with id={id} deleted."), HTTPStatus.OK
    return jsonify(error = f"Quote with id={id} not found"), HTTPStatus.NOT_FOUND


# @app.route("/quotes/count")
# def quotes_count():
#     return jsonify(count = len(quotes)), HTTPStatus.OK


# @app.route("/quotes/random")
# def random_quote() -> dict:
#     return jsonify(choice(quotes)) ,HTTPStatus.OK


# @app.route("/quotes/filter", methods=['GET'])
# def filtered_quotes() -> list[dict]:
#     args = request.args.to_dict()
#     rate_filter = args.get('rate')
#     if rate_filter:
#         args['rate'] = int(rate_filter)
#     result = quotes.copy()
#     for key in args:
#         result = list(filter(lambda x: x[key] == args[key], result))
#     return jsonify(result), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)
