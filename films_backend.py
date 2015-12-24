from flask import Flask, request
import time
import math
import json
from db import *

app = Flask(__name__)


@app.route("/get_films", methods=['GET'])
def get_films():
    try:
        per_page = int(request.args.get('per_page'))
        page = int(request.args.get('page'))
        lendb = len_db()
        if lendb % per_page > 0:
            b = 1
        else:
            b = 0
        if page < 0 or page > lendb / per_page + b:
            raise Exception()
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    print page, per_page
    items = films_from_db(page, per_page)
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items,
        'per_page': per_page,
        'page': page,
        'page_count': math.ceil(lendb / per_page + b)})


@app.route("/get_film/<id>", methods=['GET'])
def get_film_by_id(id):
    row = film_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    else:
        time.struct_time=row.duration
        return json.dumps({
            'id': row.id,
            'title': row.title.decode(encoding='ISO-8859-1', errors='strict'),
            'duration': time.struct_time,
            'year': row.year,
            'genre': row.genre.decode(encoding='ISO-8859-1', errors='strict'),
            'kinopoisk_rating': float(row.kinopoisk_rating)})


@app.route("/post_film/<id>", methods=['POST'])
def post_film(id):
    data_json = request.get_json()
    id_director = data_json['id_director']
    title = data_json['title']
    duration = data_json['duration']
    year = data_json['year']
    genre = data_json['genre']
    kinopoisk_rating = data_json['kinopoisk_rating']
    i = insert_film(id, id_director, title, duration, year, genre, kinopoisk_rating)
    if i == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    s = '/films/{'+id+'}'
    return json.dumps({
        'Location': s})


@app.route("/put_film/<id>", methods=['PUT'])
def put_film(id):
    data_json = request.get_json()
    i = 0; id_director=0; title=0; duration=0; year=0; genre=0; kinopoisk_rating=0;
    if 'id_director' in data_json:
        id_director = data_json['id_director']
    if 'title' in data_json:
        title = data_json['title']
    if 'duration' in data_json:
        duration = data_json['duration']
    if 'year' in data_json:
        year = data_json['year']
    if 'genre' in data_json:
        genre = data_json['genre']
    if 'kinopoisk_rating' in data_json:
        kinopoisk_rating = data_json['kinopoisk_rating']
    if id_director == 0 and year == 0 and kinopoisk_rating == 0 and duration == 0 and title == 0 and genre == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    if id_director != 0:
        i = update_film(id, 'id_director', id_director)
    if title != 0:
        i = update_film(id, 'title', title)
    if duration != 0:
        i = update_film(id, 'duration', duration)
    if year != 0:
        i = update_film(id, 'year', year)
    if genre != 0:
        i = update_film(id, 'genre', genre)
    if kinopoisk_rating != 0:
        i = update_film(id, 'kinopoisk_rating', kinopoisk_rating)
    if i == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    s = '/films/{'+id+'}'
    return json.dumps({
        'Location': s})


@app.route("/del_film/<id>", methods=['DELETE'])
def delete_film(id):
    row = film_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    del_film(id)
    return json.dumps({'ok' : 'ok'})


@app.route("/get_films_dir", methods=['GET'])
def get_films_dir():
    items = films_for_dir()
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items})



if __name__ == "__main__":
    app.run(debug=True, port=5103)
