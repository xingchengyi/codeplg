import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,abort
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '请输入用户名'
        elif not password:
            error = '请输入密码'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = '用户名 {} 已经被注册过了'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '用户名与密码不匹配'
        elif not check_password_hash(user['password'], password):
            error = '用户名与密码不匹配'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user['username'] != 'admin':
            abort(403)
        return view(**kwargs)
    return wrapped_view


@bp.route('/admin',methods=('POST','GET'))
@admin_required
def admin_page():
    if request.method == 'POST':
        order = request.form['order']
        db = get_db()
        answer=db.execute(
            'SELECT DISTINCT realname,type,value'
            ' FROM event JOIN user'
            ' WHERE type = ? AND user.id = event.author_id'
            ' ORDER BY author_id ASC ',(order,)
        ).fetchall()
        db.commit()
        return render_template('auth/admin.html', answer=answer)
    return render_template('auth/admin.html')

@bp.route('/<int:id>')
def user_page(id):
    db = get_db()
    info = db.execute('SELECT * FROM user'
                      ' WHERE id = ?',(id,)
                      ).fetchone()
    return render_template('auth/user_page.html',id=id,info=info)

@bp.route('/<int:id>/update',methods=('GET','POST'))
@login_required
def update_user(id):
    if id != g.user['id']:
        abort(403)
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        old_password = request.form['old_password']
        realname = request.form['realname']
        brief = request.form['brief']

        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (id,)
        ).fetchone()
        if not check_password_hash(user['password'], old_password):
            error = '旧密码错误.'
        if error is None:
            if username:
                db.execute('UPDATE user'
                           ' SET username = ?'
                           ' WHERE id = ?',(username,id)
                )
            if new_password:
                db.execute(
                    'UPDATE user'
                    ' SET password = ?'
                    ' WHERE id = ?',(generate_password_hash(new_password),id)
                )
            if realname:
                db.execute(
                    'UPDATE user'
                    ' SET realname = ?'
                    ' WHERE id = ?',(realname,id)
                )
            if brief:
                db.execute(
                    'UPDATE user'
                    ' SET brief = ?'
                    ' WHERE id = ?',(brief,id)
                )
            db.commit()
            if new_password:
                session.clear()
                return redirect(url_for('auth.login'))
            return redirect(url_for('auth.user_page',id=id))
        flash(error)

    return render_template('auth/update_user.html',id=id)