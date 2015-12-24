from flask import Flask, request
from datetime import datetime, timedelta
import math
import json
from db import *

app = Flask(__name__)


@app.route("/get_dir/<id>", methods=['GET'])
def get_dir(id):
    row = director_by_id(id)
    if row == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    else:
        return json.dumps({
            'id_director': row.id_director,
            'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
            'birthday': row.birthday,
            'country': row.country})


@app.route("/post_dir/<id>", methods=['POST'])
def post_dir(id):
    data_json = request.get_json()
    try:
        name = data_json['name']
        birthday = data_json['birthday']
        country = data_json['country']
        if name is None or birthday is None or country is None:
            raise Exception()
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    i = insert_director(id, name, birthday, country)
    if i == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    s = '/directors/{'+id+'}'
    return json.dumps({
        'Location': s})


@app.route("/put_dir/<id>", methods=['PUT'])
def put_dir(id):
    data_json = request.get_json()
    i = 0; name = 0; birthday = 0; country = 0;
    if 'name' in data_json:
        name = data_json['name']
    if 'birthday' in data_json:
        birthday = data_json['birthday']
    if 'country' in data_json:
        country = data_json['country']
    if name == 0 and birthday == 0 and country == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    if name != 0:
        i = update_director(id, 'name', name)
    if birthday != 0:
        i = update_director(id, 'birthday', birthday)
    if country != 0:
        i = update_director(id, 'country', country)
    if i == 0:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    s = '/directors/{'+id+'}'
    return json.dumps({
        'Location': s})


@app.route("/get_directors", methods=['GET'])
def get_dirs():
    per_page = int(request.args.get('per_page'))
    items = directors_from_db()
    if items is None:
        return json.dumps({'error_code': 500, 'error_msg': 'Database error'})
    lendb = len_db_dirs()
    print lendb
    if lendb % per_page > 0:
        b = 1
    else:
        b = 0
    page_count = lendb / per_page + b
    return json.dumps({
        'items': items, 'page_count': page_count})


if __name__ == "__main__":
    app.run(debug=True, port=5102)
