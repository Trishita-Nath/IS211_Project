from flask import Flask, render_template, request, redirect, \
    flash, session, g, abort, url_for
import os.path
from datetime import datetime
import sqlite3
from contextlib import closing


DEBUG = True
USERNAME = ''
DATABASE = 'blog_posts.db'
SECRET_KEY = 'development key'


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


connect_db()
#init_db()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def home_page():
    return render_template('index.html', entries=get_posts())


@app.route('/post/<int:id>')
def show_post(id):
    return render_template('post.html', post=get_post(id))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO entries (title, content, user) VALUES (?, ?, ?)',
        [request.form['title'], request.form['content'], app.config['USERNAME']])
    g.db.commit()
    return redirect('/dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        rec = get_admin(request.form['username'])
        if rec == None:
            error = 'Incorrect username'
        elif request.form['password'] != rec['password']:
            error = 'Incorrect password'
        else:
            session['logged_in'] = True
            app.config['USERNAME'] = rec['username']
            return redirect('/dashboard')
    return render_template('login.html', error=error)

    
def get_admin(username):
    cur = g.db.execute('SELECT username, password,\
        displayName from users where username =?', [(username)])
    row = cur.fetchone()
    if row != None:
        return dict(username=row[0], password=row[1], displayName=row[2])
    else:
        return None


@app.route('/save', methods=['POST'])
def save():
    entryId = int(request.form['id'])
    cur = g.db.execute(
        'UPDATE entries SET title=?, content=?, timeEntry=? WHERE id=?',\
        (request.form['title'], request.form['content'],
            request.form['timeEntry'], entryId))
    g.db.commit()
    return redirect('/dashboard')


@app.route('/edit', methods=['POST'])
def edit():
    entryId = int(request.form['id'])
    return render_template('edit.html', entry=get_post(entryId))


@app.route('/delete', methods=['POST'])
def delete():
    entryId = int(request.form['id'])
    cur = g.db.execute('DELETE FROM entries WHERE id =?', [(entryId)])
    g.db.commit()
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    app.config['USERNAME'] = ''
    return redirect('/')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', entries=get_posts(), appConfig=app.config)


def get_posts():
    cur = g.db.execute('SELECT title, content, id, timeEntry,\
        user from entries order by id desc')
    return[dict(title=row[0],content=row[1],id=row[2],timeEntry=row[3],user=row[4],permalink='/post/' + str(row[2]))for row in cur.fetchall()]


def get_post(id):
    cur = g.db.execute('SELECT title, content, id, timeEntry,\
        user from entries where id =?', [(id)])
    row = cur.fetchone()
    return dict(title=row[0],content=row[1],id=row[2],timeEntry=row[3],user=row[4])





if __name__ == "__main__":
    app.run()