from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.db import get_db


bp = Blueprint('profile', __name__)
@bp.route('/profile')
def index():
    db = get_db()
    profile = db.execute(
        'SELECT id,title,body,created'
        ' FROM post WHERE title = ?',('#PROFILE#',)
    ).fetchone()
    return render_template('profile/index.html',profile=profile)

