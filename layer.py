from flask import Flask, request
import requests
import json

app = Flask(__name__)


def get_session_url(url_part):
    return "http://localhost:5104/" + url_part


def get_directors_url(url_part):
    return "http://localhost:5102/" + url_part


def get_films_url(url_part):
    return "http://localhost:5103/" + url_part


def check_connection(login, token):
    url = get_session_url("check_connection?login={0}&token={1}".format(login, token))
    result = requests.get(url).json()
    return 'ok' in result


@app.route("/add_user", methods=['POST'])
def add_user():
    data_json = request.get_json()
    url = get_session_url("add_user")
    headers = {'Content-type': 'application/json'}
    result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/authorize", methods=['GET'])
def authorize():
    phone = request.args.get('phone')
    password = request.args.get('password')
    print phone, password
    if phone is None or password is None:
        return json.dumps({'error_code': 400, 'error_msg': 'No phone or password'}, indent=4), 400
    url = get_session_url("authorize") + "?phone={0}&password={1}".format(phone, password)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/get_films", methods=['GET'])
def get_films():
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    print page, per_page
    url = get_films_url("get_films") + "?page={0}&per_page={1}".format(page, per_page)
    result = requests.get(url).json()
    print result
    json1 = json.dumps(result)
    return json1


@app.route("/get_me", methods=['GET'])
def get_me():
    phone = request.args.get('phone')
    url = get_session_url("get_me") + "?phone={0}".format(phone)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/get_film/<id>", methods=['GET'])
def get_film_by_id(id):
    url = get_films_url("get_film") + "/{0}".format(id)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/post_film/<id>", methods=['POST'])
def post_film(id):
    url = get_films_url("post_film") + "/{0}".format(id)
    data_json = request.get_json()
    headers = {'Content-type': 'application/json'}
    result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/put_film/<id>", methods=['PUT'])
def put_film(id):
    url = get_films_url("put_film") + "/{0}".format(id)
    data_json = request.get_json()
    print data_json
    headers = {'Content-type': 'application/json'}
    result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/del_film/<id>", methods=['DELETE'])
def del_film(id):
    url = get_films_url("del_film") + "/{0}".format(id)
    result = requests.delete(url).json()
    json1 = json.dumps(result)
    return json1


@app.route("/get_dir/<id>", methods=['GET'])
def get_dir(id):
    url = get_directors_url("get_dir") + "/{0}".format(id)
    result = requests.get(url).json()
    print result
    json1 = json.dumps(result)
    return json1


@app.route("/post_dir/<id>", methods=['POST'])
def post_dir(id):
    url = get_directors_url("post_dir") + "/{0}".format(id)
    data_json = request.get_json()
    headers = {'Content-type': 'application/json'}
    result = requests.post(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/put_dir/<id>", methods=['PUT'])
def put_dir(id):
    url = get_directors_url("put_dir") + "/{0}".format(id)
    data_json = request.get_json()
    headers = {'Content-type': 'application/json'}
    result = requests.put(url, data=json.dumps(data_json), headers=headers).json()
    json1 = json.dumps(result)
    return json1


@app.route("/get_directors", methods=['GET'])
def get_dirs():
    try:
        per_page_dir = int(request.args.get('per_page'))
        url = get_directors_url("get_directors") + "?per_page={0}".format(per_page_dir)
        result = requests.get(url).json()
        page_dir = int(request.args.get('page'))
    except:
        return json.dumps({'error_code': 400, 'error_msg': 'Bad Request'})
    url = get_films_url("get_films_dir")
    result_film = requests.get(url).json()
    o1 = result_film['items'];  a1 = o1[1]
    o2 = result['items']; a2 =o2[1]
    items = []
    for i1 in range(0, len(o1)):
        for i2 in range(0, len(o2)):
            a1 = o1[i1]; a2 = o2[i2]
            if a1['id_director']== a2['id_director']:
                items.append({
                'id_director': a2['id_director'],
                'name': a2['name'],
                'title': a1['title']})
    items = items[(page_dir-1)*per_page_dir:page_dir*per_page_dir]
    if items is None:
        return json.dumps({'error_code': 404, 'error_msg': 'Not Found'})
    return json.dumps({
        'items': items,
        'per_page': per_page_dir,
        'page': page_dir})


@app.route("/check_session", methods=['GET'])
def check_ss():
    phone = request.args.get('phone')
    code = request.args.get('code')
    url = get_session_url("check_session") + "?phone={0}&code={1}".format(phone, code)
    result = requests.get(url).json()
    json1 = json.dumps(result)
    return json1

if __name__ == "__main__":
    app.run(debug=True, port=5101)
