import time
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db
from flask_uploads import UploadSet,IMAGES
from flask_uploads import configure_uploads,patch_request_class
import os
from flask import current_app as app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import SubmitField,MultipleFileField,TextAreaField,RadioField
from PIL import Image
import random,string
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired, StopValidation
from flask_wtf.file import abc

bp = Blueprint('daily', __name__,url_prefix='/daily')

photos = UploadSet('photos',IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(),'flaskr','static')
configure_uploads(app,photos)
app.config['MAX_CONTENT_LENGTH'] = 10*1024*1024
patch_request_class(app,size=None)

@bp.route('/')
def index():
    render_list = []
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    for post in posts:
        if post['title'][0:7] != '#DAILY#':
            continue
        thumb_list = post['title'][7:].split('*')
        body = post['body']
        created = post['created']
        username = post['username']
        id = post['id']
        author_id = post['author_id']
        render_list.append((body,thumb_list,created,username,id,author_id))
    print(render_list)
    return render_template('daily/index.html',render_list=render_list)

class MultiFileAllowed(FileAllowed):
    def __call__(self, form, field):
        if not field.data:
            print("POS0")
            return
        for d in field.data:
            if not isinstance(d,FileStorage):
                return
            if d.filename == '':
                return
        for f in form.data['photo']:
            filename = f.filename.lower()
            if isinstance(self.upload_set, abc.Iterable):
                print("POS4")
                if any(filename.endswith('.' + x) for x in self.upload_set):
                    print("pos validate")
                    return

                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension: {extensions}'
                ).format(extensions=', '.join(self.upload_set)))

            if not self.upload_set.file_allowed(field.data, filename):
                raise StopValidation(self.message or field.gettext(
                    'File does not have an approved extension.'
                ))

class UploadForm(FlaskForm):
    photo = MultipleFileField(label='要上传图片吗:)',validators=[MultiFileAllowed(photos, "只能上传图片")])
    description = TextAreaField(label="写点什么吧")
    flu = RadioField(label="有流感的症状吗",validators=[DataRequired('请选择一个')],render_kw={'class': 'form-control'},choices=[(1,'完全没事'),(2,'有点咳嗽')],default=1,coerce=int)
    submit = SubmitField('提交')

@bp.route('/new',methods=('GET','POST'))
@login_required
def upload():
    form = UploadForm()
    thumb_list = []
    # clear_thumbnail(app.config['UPLOADED_PHOTOS_DEST'])
    if form.validate_on_submit():

        for f in request.files.getlist('photo'):
            if f.filename == '':
                break
            suffix = os.path.splitext(f.filename)[1].lower()
            filename = ''.join(random.sample(string.ascii_letters + string.digits,15))+suffix
            photos.save(f,name = filename)
            pathname = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],filename)
            img = Image.open(pathname)
            img.thumbnail((128,128))
            img.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],'#'+filename))
            thumb_url = photos.url('#'+filename)
            thumb_list.append(thumb_url)

        flu_status = form.data['flu']
        daily_content = form.data['description']
        thumb_string = '*'.join(i for i in thumb_list)
        thumb_string = "#DAILY#"+thumb_string
        db = get_db()
        db.execute(
            'INSERT INTO post(author_id,body,title)'
            ' VALUES (?,?,?)',(g.user['id'],daily_content,thumb_string)
        )
        date = time.strftime("%Y%m%d", time.localtime())
        date = 'aiw' + date
        if flu_status == 1:
            db.execute(
                'INSERT INTO event(type,value,author_id)'
                ' VALUES (?,?,?)', (date, "well", g.user['id'])
            )
        else:
            db.execute(
                'INSERT INTO event(type,value,author_id)'
                ' VALUES (?,?,?)', (date, "NOTWELL", g.user['id'])
            )
        db.commit()
        error = "提交成功"
        flash(error)
    return render_template('daily/new.html', form=form, img_list=thumb_list)

def clear_thumbnail(path_to_thumbnail):
    for root,dirs,filename in os.walk(path_to_thumbnail):
        for f in filename:
            if f[0] == '#':
                os.remove(os.path.join(path_to_thumbnail,f))
        break
