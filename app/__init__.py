from flask import Flask, render_template, request, session, url_for, redirect
import pymysql

app = Flask(__name__)

# conn = pymysql.connect(
#     host= 'localhost',
#     user="root",
#     password='root',
#     db='meetup',
#     charset='utf8mb4',
#     cursorclass=pymysql.cursors.DictCursor
# )

app.secret_key="some key"

from app import views



