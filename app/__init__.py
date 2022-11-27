from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import pymysql
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"
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
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models
    from .models import User

    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app



