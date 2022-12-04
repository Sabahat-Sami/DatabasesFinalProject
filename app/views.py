from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from datetime import datetime
from app import conn

views = Blueprint('views', __name__)


def executeSearchQuery(arrival, departure):
    cursor = conn.cursor()
    if arrival == "" and departure == "":
        query = 'SELECT * FROM flights'
        cursor.execute(query)
    elif arrival != "" and departure == "":
        query = 'SELECT * FROM flights WHERE arrival_airport=%s'
        cursor.execute(query, (arrival))
    elif arrival == "" and departure != "":
        query = 'SELECT * FROM flights WHERE departure_airport=%s'
        cursor.execute(query, (departure))
    else:
        query = 'SELECT * FROM flights WHERE arrival_airport=%s and departure_airport=%s'
        cursor.execute(query,(arrival, departure))
    data = cursor.fetchall()
    cursor.close()
    return data

@views.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == "POST":
        source = request.form.get('source')
        print('source: ',source)
        destination = request.form.get('destination')
        date = request.form.get('date')

        data = executeSearchQuery(source, destination)
        urls = [f'purchase_flight/'+str(flight['flight_number']) for flight in data]
        if not data:
            flash("No flights found!", category='error')
        return render_template('home.html', user=session, data=zip(data, urls))

    return render_template('home.html', user=session, data=None)


@views.route('/view_flights', methods=['GET'])
def view_flights():
    if session['user'] and session['customerOrStaff'] == 'customer':
        cursor = conn.cursor()
        query = 'SELECT DISTINCT flight_number, flight_status, arrival_airport, departure_airport FROM tickets NATURAL JOIN flights where email = %s'
        cursor.execute(query, (session['user']))
        data = cursor.fetchall()
        cursor.close()
        return render_template('view_flights.html', user=session, flights=data)
    return redirect(url_for('views.home'))

@views.route('/purchase_flight/<flight_number>', methods=['GET', 'POST'])
def purchase_flight(flight_number):
    if session['user'] and session['customerOrStaff'] == 'customer':
        cursor = conn.cursor()
        query = 'SELECT * FROM flights where flight_number = %s'
        cursor.execute(query, (flight_number))
        data = cursor.fetchone()
        cursor.close()
        sold_price = "$" + str(round(data['base_price'] * 1.075, 2))
        if request.method == "POST":
            name = request.form.get("name")
            credit_number = request.form.get("credit_number")
            credit_expiration = request.form.get("credit_expiration")
            credit_or_debit = request.form.get("card_type")
            credit_expiration = credit_expiration.strip() + " 00:00:00"
            try:
                credit_expiration = datetime.strptime(credit_expiration, '%Y-%m-%d %H:%M:%S')
            except:
                flash("date of birth must be in the format of YYYY-MM-DD", category="error")
                return render_template('purchaseFlights.html')
            cursor = conn.cursor()
            query = "SELECT MAX(ticket_id) as new_id FROM tickets"
            cursor.execute(query)
            data = cursor.fetchone()
            new_id = data['new_id']
            if new_id is None:
                new_id = 1
            else:
                new_id += 1
            date_time_purchased = datetime.now()
            query = "SELECT * FROM flights WHERE flight_number = %s"
            cursor.execute(query, (flight_number))
            data = cursor.fetchone()
            query = "SELECt * FROM owns WHERE identification_number = %s"
            cursor.execute(query, (data['identification_number']))
            airline= cursor.fetchone()['name']
            cursor.close()
            if credit_or_debit.lower() != "credit" and credit_or_debit.lower() != "debit":
                print(credit_or_debit.lower())
                flash("Please enter credit or debit as card type", category='error')
            else:
                cursor = conn.cursor()
                query = "INSERT INTO `tickets` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (new_id, float(sold_price.strip("$")), date_time_purchased, credit_expiration, name, credit_number, credit_or_debit, session['user'], data['flight_number'], data['flight_status'], airline, data['identification_number']))
                conn.commit()
                cursor.close()
                flash('Flight purchased!', category='success')
                return redirect(url_for('views.home'))
        return render_template('purchaseFlights.html', user=session, data=sold_price)
    return redirect(url_for('views.home'))
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
