from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == "POST":
        source = request.form.get('source')
        destination = request.form.get('destination')
        date = request.form.get('date')

        search = []
        ############################
        # fetch data and display on front page(probably collect in a list and on home.html
        # if list not empty, then display
        ############################
        if not search:
            flash("No flights found!", category='error')
        return render_template('home.html', user=session, search=search)

    return render_template('home.html', user=session, search=None)
