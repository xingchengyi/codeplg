from flask import Blueprint,flash,g,redirect,render_template,request,url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('event',__name__)
@bp.route('/event',methods = ('GET','POST'))
@login_required
def index():
    if request.method == 'POST':
        error = None
        type = request.form['type']
        value = request.form['value']

        if not type:
            error = 'event type是需要输入的说~'
        if not value:
            error = '请输入值QwQ'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO event (type,value,author_id)'
                ' VALUES (?,?,?)',(type,value,g.user['id'])
            )
            db.commit()
    return render_template('event/index.html')