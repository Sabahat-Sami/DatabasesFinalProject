from flask import Flask

from os import path
import pymysql


conn = pymysql.connect(
            host="localhost", 
            port=8889,
            user="root",
            password="root",
            db="3083FinalProject",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dasdasd 2ffeffdsf berggertf hgedgdfss'


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app



