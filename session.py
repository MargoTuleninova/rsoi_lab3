from flask import Flask, request
import random
import string
import json
from db import *

app = Flask(__name__)

@app.route("/add_user", methods=['POST'])
def add_user():
    data_json = request.get_json()
    print data_json
    name = data_json['name']
    phone = data_json['phone']
    password = data_json['password']
    email = data_json['email']
    if user_exist(phone):
        return json.dumps({'error_code': 400, 'error_msg': 'User already exists'}, {
        'Content-Type': 'application/json;charset=UTF-8',
    })

    i = insert_user(name, password, phone, email)
    if i == 0:
        return json.dumps({'error_code': 500, 'error_msg': 'Database error'})
    return json.dumps({'ok': 'ok'})


@app.route("/authorize", methods=['GET'])
def authorize():
    phone = request.args.get('phone')
    password = request.args.get('password')
    if user_exist(phone, password):
        code = ''.join(random.choice(string.lowercase) for i in range(30))
        i = code_insert(code, phone)
        if i==0:
            return json.dumps({'error_code': 500, 'error_msg': 'Database Error'})
        return json.dumps({'code': code})
    return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})


@app.route("/get_me", methods=['GET'])
def get_me():
    phone = request.args.get('phone')
    row = get_me_db(phone)
    print row
    if row == 0:
        return json.dumps({'error_code': 500, 'error_msg': 'Server Error'})
    return json.dumps({
            'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
            'mail': row.mail,
            'phone': row.phone})


@app.route("/check_session", methods=['GET'])
def check_ss():
    phone = request.args.get('phone')
    code = request.args.get('code')
    i = user_connected(phone, code)
    if i == 0:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'})
    else:
        return json.dumps({'ok': 'ok'})

if __name__ == "__main__":
    app.run(debug=True, port=5104)
