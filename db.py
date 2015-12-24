import pyodbc
from datetime import datetime, timedelta


def users_db_conn():
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=Lenovo-Margo;DATABASE=users;')
    cursor = cnxn.cursor()
    return cursor;


def films_db_conn():
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=Lenovo-Margo;DATABASE=Films;')
    cursor = cnxn.cursor()
    return cursor;


def user_exist(phone, password):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where phone='" + phone+"'")
    row = cursor.fetchone()
    if row:
        if row.parol.find(password)!=-1:
            return 1
    return 0


def insert_user(name, password, phone, email):
    cursor = users_db_conn()
    cursor.execute("insert into dbo.UsersInfo values ('"+phone+"','"+name+"','"+email+"','','"+password+"','','','')")
    cursor.commit()
    return;


def code_insert(code, phone):
    try:
        cursor = users_db_conn()
        cursor.execute("update dbo.UsersInfo set access_token='"+code+"' where phone='" + phone+"'")
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1;


def len_db():
    cursor = films_db_conn()
    cursor.execute("select count(*) from dbo.main")
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0;

def films_from_db(page, per_page):
    items = []
    cursor = films_db_conn()
    cursor.execute("select * from dbo.main")
    rows = cursor.fetchall()
    for row in rows:
        if row.id <= page * per_page:
            if row.id > (page - 1) * per_page:
                text = row.title.decode(encoding='ISO-8859-1', errors='strict')
                items.append({
                'id': row.id,
                'id_director': row.id_director,
                'title': text,
                'kinopoisk_rating': float(row.kinopoisk_rating),
                })
        if row.id >= (page + 1) * per_page:
            break
    return items;


def film_by_id(id):
    cursor = films_db_conn()
    cursor.execute("select * from dbo.main where id=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;


def len_db_dirs():
    count = 0;
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors")
    rows = cursor.fetchall()
    for row in rows:
                count += 1
    return count;

def directors_from_db():
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors")
    rows = cursor.fetchall()
    items= []
    for row in rows:
            items.append({
            'id_director': row.id_director,
            'name': row.name.decode(encoding='ISO-8859-1', errors='strict'),
            })
    return items;


def insert_film(id, id_director, title, duration, year, genre, kinopoisk_rating):
    cursor = films_db_conn()
    try:
        cursor.execute("insert into dbo.main values ("+id+", "+id_director+",'"+title+"','"+duration+"', "+year+", '"+genre+"', "+kinopoisk_rating+")")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1


def update_film(id, str, value):
    cursor = films_db_conn()
    try:
        if str == 'title' or str == 'duration' or str == 'genre':
            cursor.execute("update dbo.main set "+str+"='"+value+"' where id="+id)
            cursor.commit()
        else:
            cursor.execute("update dbo.main set "+str+"="+value+" where id="+id)
            cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1


def del_film(id):
    cursor = films_db_conn()
    cursor.execute("delete from dbo.main where id="+id)
    cursor.commit()


def director_by_id(id):
    cursor = films_db_conn()
    cursor.execute("select * from dbo.directors where id_director=" + id)
    row = cursor.fetchone()
    if row:
        return row
    else:
        return 0;


def insert_director(id, name, birthday, country):
    cursor = films_db_conn()
    try:
        cursor.execute("insert into dbo.directors values ("+id+", '"+name+"', '"+birthday+"', '"+country+"')")
        cursor.commit()
    except pyodbc.IntegrityError:
        return 0
    return 1


def update_director(id, str, value):
    cursor = films_db_conn()
    try:
        cursor.execute("update dbo.directors set "+str+"='"+value+"' where id_director="+id)
        cursor.commit()
    except ValueError:
        return 1
    except pyodbc.IntegrityError:
        return 0
    return 1

def films_for_dir():
    items = []
    cursor = films_db_conn()
    cursor.execute("select * from dbo.main")
    rows = cursor.fetchall()
    for row in rows:
            text = row.title.decode(encoding='ISO-8859-1', errors='strict')
            items.append({
            'id_director': row.id_director,
            'title': text,
            })
    return items;


def user_connected(phone, code):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where phone='" + phone+"'")
    row = cursor.fetchone()
    if row:
        if row.access_token == code:
            return 1
    return 0


def get_me_db(phone):
    cursor = users_db_conn()
    cursor.execute("select * from dbo.UsersInfo where phone='" + phone+"'")
    row = cursor.fetchone()
    if row:
        return row
    return 0