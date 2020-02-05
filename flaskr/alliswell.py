from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import time
bp = Blueprint('aiw',__name__)

@bp.route('/alliswell',methods=('GET','POST'))
@login_required
def index():
    if request.method=='POST':
        error = None
        check = request.form['check']
        if not check:
            error="请选择一个"
        if error is not None:
            flash(error)
        else:
            db = get_db()
            date = time.strftime("%Y%m%d", time.localtime())
            date = 'aiw' + date
            db.execute(
                'INSERT INTO event(type,value,author_id)'
                ' VALUES (?,?,?)',(date,check,g.user['id'])
            )
            db.commit()
    return render_template('aiw/index.html')