from flask import Flask, render_template, request, session, redirect, url_for, make_response
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)


def get_layer_url(url_part):
    return "http://localhost:5101/" + url_part


def get_data_from_cookies():
    expired = session.get('expired')
    if expired is None:
        return None, None
    if expired < datetime.now():
        clear_data_in_cookies()
        return 0, 0
    return session.get('login'), session.get('code')


def set_data_to_cookies(login, code):
    session['login'] = login
    session['code'] = code
    session['expired'] = datetime.now() + timedelta(minutes=10)


def clear_data_in_cookies():
    session.pop('login', None)
    session.pop('code', None)
    session.pop('expired', None)


@app.route("/")
def home():
    if not ('login' in session and 'code' in session):
        return redirect(url_for('authorization_form'))

    return render_template("main.html")


@app.route('/authorize', methods=['GET'])
def authorization_form():
    return render_template('authorize.html')


@app.route("/authorize", methods=['POST'])
def authorization():
    if 'reg' in request.form:
        return redirect(url_for('registration'))
    if 'go' in request.form:
        return redirect(url_for('main_form'))

    if not ('login' in session and 'code' in session):
        phone = str(request.form.get('phone'))
        password = str(request.form.get('password'))
        url = get_layer_url("authorize") + "?phone={0}&password={1}".format(phone, password)
        result = requests.get(url).json()
        if 'error_code' in result:
            code = result['error_code']
            msg = result['error_msg']
            return json.dumps({'message': msg, 'error': code}, indent=4), code
        session.permanent = True
        set_data_to_cookies(phone, result['code'])
        response = make_response(redirect(url_for('main_form')))
        response.set_cookie('Expires', "{0}".format(datetime.now()+timedelta(minutes=10)))
        response.set_cookie('token', result['code'])
        response.set_cookie('login', phone)
        print response
        return response

    return redirect(url_for('main_form'))


@app.route('/register', methods=['GET'])
def registration():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    if not name:
        return render_template('fail_registration.html', reason='Empty login not allowed.')

    password = request.form['password']
    if len(password) < 6:
        return render_template('fail_registration.html', reason='Password is too short')

    email = request.form['email']
    phone = request.form['phone']

    url = get_layer_url("add_user")
    data = {'name': name, 'password': password, 'email': email, 'phone': phone}
    headers = {'Content-type': 'application/json'}

    result = requests.post(url, data=json.dumps(data), headers=headers).json()

    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    return render_template("authorize.html")


@app.route("/logout", methods=['GET'])
def logout():
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return render_template("main.html")
    clear_data_in_cookies()
    response = make_response(redirect(url_for('main_form')))
    response.delete_cookie('login')
    response.delete_cookie('Expires')
    response.delete_cookie('token')
    return response


@app.route('/main', methods=['GET'])
def main_form():
    return render_template("main.html")


@app.route('/main', methods=['POST'])
def main():
    if 'get_films' in request.form:
        return redirect(url_for('get_films'))
    if 'film_by_id' in request.form:
        return render_template("ID_film.html")
    if 'p_films' in request.form:
        return render_template("Film_data.html")
    if 'get_dirs' in request.form:
        return redirect(url_for('get_directors'))
    if 'dir_by_id' in request.form:
        return render_template("ID_dir.html")
    if 'p_dirs' in request.form:
        return render_template("Dir_data.html")
    if 'me' in request.form:
        return redirect(url_for('me'))
    if 'logout' in request.form:
        return redirect(url_for('logout'))
    return '', 200


@app.route('/films', methods=['GET'])
def get_films():
    global page
    next = request.args.get('next')
    prev = request.args.get('prev')
    if prev is not None:
        page -= 1
    elif next is not None:
        page += 1
    else:
        page = 1
    per_page = 5
    url = get_layer_url("get_films") + ("?page={0}&per_page={1}".format(page, per_page))
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    res = result['items']
    return render_template("films_show.html", films=res, page=page)


@app.route('/film', methods=['GET'])
def film_by_id():
    id = int(request.args.get('id'))
    show = request.args.get('show')
    delete = request.args.get('delete')
    res = 200
    if delete is not None:
        res = delete_film(id)
    if show is not None:
        res = get_film_by_id(id)
    return res


@app.route('/films/<id>', methods=['GET'])
def get_film_by_id(id):
    responce = redirect('/')

    print responce
    phone, code = get_data_from_cookies()
    print phone, code
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_layer_url("get_film") + ("/{0}".format(id))
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    return render_template("film_by_id.html", films=result)


@app.route('/films/<id>', methods=['DELETE'])
def delete_film(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_layer_url("del_film") + "/{0}".format(id)
    result = requests.delete(url)
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    return '', 200


@app.route('/film_p', methods=['GET'])
def film_p():
    id = int(request.args.get('id'))
    if id == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'}), 400
    post = request.args.get('post')
    put = request.args.get('put')
    res = 200
    if post is not None:
        res = post_film(id)
    if put is not None:
        res = put_film(id)
    return res


@app.route('/films/<id>', methods=['POST'])
def post_film(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    id_director = request.args.get('id_director')
    title = request.args.get('title')
    duration = request.args.get('duration')
    year = request.args.get('year')
    genre = request.args.get('genre')
    kinopoisk_rating = request.args.get('kinopoisk_rating')
    print id, id_director, title, duration, year, genre, kinopoisk_rating
    if id_director is None or year is None or kinopoisk_rating is None:
            return '', 400
    if duration is None or title is None or genre is None:
            return '', 400
    url = get_layer_url("post_film") + "/{0}".format(id)
    headers = {'Content-type': 'application/json'}
    data = {'id': id, 'id_director': id_director, 'title': title, 'duration': duration,
            'year': year, 'genre': genre, 'kinopoisk_rating': kinopoisk_rating}

    result = requests.post(url, data=json.dumps(data), headers=headers).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    location = result['Location']

    return json.dumps({'Location': location}, indent=4), 201


@app.route('/films/<id>', methods=['PUT'])
def put_film(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    id_director = request.args.get('id_director')
    title = request.args.get('title')
    duration = request.args.get('duration')
    year = request.args.get('year')
    genre = request.args.get('genre')
    kinopoisk_rating = request.args.get('kinopoisk_rating')
    if id_director == '' and year== '' and kinopoisk_rating == '' and duration == '' and title == '' and genre == '':
        return '', 400
    url = get_layer_url("put_film") + "/{0}".format(id)
    if id_director != '':
        data = {'id': id, 'id_director': id_director}
    if title != '':
        data = {'id': id, 'title': title}
    if duration != '':
        data = {'id': id, 'duration': duration}
    if year != '':
        data = {'id': id, 'year': year}
    if genre != '':
        data = {'id': id, 'genre': genre}
    if kinopoisk_rating != '':
        data = {'id': id, 'kinopoisk_rating': kinopoisk_rating}
    headers = {'Content-type': 'application/json'}
    print data
    result = requests.put(url, data=json.dumps(data), headers=headers).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    location = result['Location']

    return json.dumps({'Location': location}, indent=4), 200


@app.route('/directors', methods=['GET'])
def get_directors():
    global page
    next = request.args.get('next')
    prev = request.args.get('prev')
    if prev is not None:
        page -= 1
    elif next is not None:
        page += 1
    else:
        page = 1
    per_page = 5
    url = get_layer_url("get_directors") + ("?page={0}&per_page={1}".format(page, per_page))

    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    res = result['items']
    return render_template("dirs_show.html", dirs=res, page=page)


@app.route('/dir', methods=['GET'])
def dir_by_id():
    id = int(request.args.get('id'))
    return get_dir_by_id(id)


@app.route('/directors/<id>', methods=['GET'])
def get_dir_by_id(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    url = get_layer_url("get_dir") + "/{0}".format(id)

    result = requests.get(url).json()
    print result
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    return render_template("dir_by_id.html", dir=result)


@app.route('/dir_p', methods=['GET'])
def dir_p():
    id = int(request.args.get('id_director'))
    if id == 0:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'}), 400
    post = request.args.get('post')
    put = request.args.get('put')
    res = 200
    if post is not None:
        res = post_director(id)
    if put is not None:
        res = put_director(id)
    return res


@app.route('/directors/<id>', methods=['POST'])
def post_director(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    name = request.args.get('name')
    birthday = request.args.get('birthday')
    country = request.args.get('country')
    if name is None or birthday is None or country is None:
        return '', 400

    url = get_layer_url("post_dir") + "/{0}".format(id)
    headers = {'Content-type': 'application/json'}
    data = {'name': name, 'birthday': birthday, 'country': country}

    result = requests.post(url, data=json.dumps(data), headers=headers).json()
    print result
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    location = result['Location']
    return json.dumps({'Location': location}, indent=4), 201


@app.route('/directors/<id>', methods=['PUT'])
def put_director(id):
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    name = request.args.get('name')
    birthday = request.args.get('birthday')
    country = request.args.get('country')
    if name == '' and birthday == '' and country == '':
        return '', 400

    url = get_layer_url("put_dir") + "/{0}".format(id)
    if name != '':
        data = {'id_director': id, 'name': name}
    if birthday != '':
        data = {'id_director': id, 'birthday': birthday}
    if country != '':
        data = {'id_director': id,'country': country}
    headers = {'Content-type': 'application/json'}

    result = requests.put(url, data=json.dumps(data), headers=headers).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    location = result['Location']

    return json.dumps({'Location': location}, indent=4), 200


@app.route('/me', methods=['GET'])
def me():
    phone, code = get_data_from_cookies()
    if phone is None or code is None:
        return json.dumps({'error_code': 401, 'error_msg': 'UnAuthorized'}), 401
    if phone == 0 or code == 0:
        return json.dumps({'error_code': 498, 'error_msg': 'Token expired'}), 498
    url = get_layer_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code
    print result
    url = get_layer_url("get_me") + "?phone={0}".format(phone)
    result = requests.get(url).json()

    if 'error_code' in result:
        code = result['error_code']
        msg = result['error_msg']
        return json.dumps({'message': msg, 'error': code}, indent=4), code

    return json.dumps(result, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }


if __name__ == "__main__":
    page = 1
    app.secret_key = os.urandom(24)
    app.run(debug=True, port=5100)
