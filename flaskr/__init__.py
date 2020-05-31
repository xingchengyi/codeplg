import os

from flask import Flask
from datetime import datetime
import time

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'
    # @app.route('/')
    # def index():
    #     return 'Index Page'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import attd
    app.register_blueprint(attd.bp)

    from . import event
    app.register_blueprint(event.bp)

    from . import alliswell
    app.register_blueprint(alliswell.bp)
    from . import profile
    app.register_blueprint(profile.bp)

    def strftime_to_localtime(t):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t.timestamp()+28800))
    app.add_template_global(strftime_to_localtime)

    with app.app_context():
        from . import daily
        app.register_blueprint(daily.bp)
    return app