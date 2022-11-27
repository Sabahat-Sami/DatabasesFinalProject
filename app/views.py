from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for,session




views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    print(session)
    return render_template('home.html', user=session)

