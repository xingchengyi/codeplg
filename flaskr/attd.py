from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('attd',__name__)

@bp.route('/attd',methods = ('GET',"POST"))
@login_required
def index():
    db = get_db()
    user_id = session.get('user_id')
    stat = db.execute(
        'SELECT time,id,type'
        ' FROM attendance'
        ' WHERE id = (?)'
        ' ORDER BY time DESC',(user_id,)
    ).fetchone()

    if stat is None or stat['type'] == 0:
        status = 0
    else:
        status = 1
    if stat is None:
        time = 0
    else:
        time = stat['time']
    if request.method == 'POST':
        db.execute(
            'INSERT INTO attendance(id,type)'
            ' VALUES (?,?)',(user_id,status ^ 1)
        )
        db.commit()

        return redirect(url_for('attd.index'))

    return render_template('attd/index.html',status = status,time = time)
