from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session

from app import conn

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == "POST":
        source = request.form.get('source')
        print('source: ',source)
        destination = request.form.get('destination')
        date = request.form.get('date')

        cursor = conn.cursor()
        query = 'SELECT * FROM flights WHERE name = %s'
        cursor.execute(query, (source))
        data = cursor.fetchall()
        cursor.close()

        if not data:
            flash("No flights found!", category='error')
        return render_template('home.html', user=session, data=data)

    return render_template('home.html', user=session, data=None)


@views.route('/view_flights', methods=['GET'])
def view_flights():
    cursor = conn.cursor()
    query = 'SELECT * FROM flights'
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    cursor.close()
    return render_template('view_flights.html', user=session, flights=data)


@views.route('/create_new_flight', methods=['GET', 'POST'])
def create_new_flight():
    return render_template('home.html', user=session)


@views.route('/change_flight_status', methods=['GET', 'POST'])
def change_flight_status():
    return render_template('home.html', user=session, search=None)


@views.route('/add_new_airplane', methods=['GET', 'POST'])
def add_new_airplane():
    return render_template('home.html', user=session, search=None)


@views.route('/add_new_airport', methods=['GET', 'POST'])
def add_new_airport():
    return render_template('home.html', user=session, search=None)


@views.route('/view_flight_ratings', methods=['GET', 'POST'])
def view_flight_ratings():
    return render_template('home.html', user=session, search=None)


@views.route('/view_frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
    return render_template('home.html', user=session, search=None)


@views.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    return render_template('home.html', user=session, search=None)


@views.route('/view_revenue', methods=['GET', 'POST'])
def view_revenue():
    return render_template('home.html', user=session, search=None)
