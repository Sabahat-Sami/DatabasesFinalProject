from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app import conn

views = Blueprint('views', __name__)


def executeSearchQuery(arrival, departure):
    cursor = conn.cursor()
    if arrival == "" and departure == "":
        query = 'SELECT flights.flight_number, flights.base_price, flights.departure_airport, flights.arrival_airport, departs.date, departs.time, arrives.date, arrives.time FROM flights, departs, arrives WHERE flights.flight_number = departs.flight_number AND flights.flight_number = arrives.flight_number AND %s < departs.date AND %s < departs.time'
        cursor.execute(query, (datetime.today(), datetime.now().strftime("%H:%M:5S")))
    elif arrival != "" and departure == "":
        query = 'SELECT * FROM flights, departs, arrives WHERE flights.flight_number = departs.flight_number = arrives.flight_number AND %s < departs.date AND %s < departs.time AND arrival_airport=%s'
        cursor.execute(query, (datetime.today(), datetime.now().strftime("%H:%M:5S"),arrival))
    elif arrival == "" and departure != "":
        query = 'SELECT * FROM flights, departs, arrives WHERE flights.flight_number = departs.flight_number = arrives.flight_number AND %s < departs.date AND %s < departs.time AND departure_airport=%s'
        cursor.execute(query, (datetime.today(), datetime.now().strftime("%H:%M:5S"),departure))
    else:
        query = 'SELECT * FROM flights, departs, arrives WHERE flights.flight_number = departs.flight_number = arrives.flight_number AND %s < departs.date AND %s < departs.time AND arrival_airport=%s AND departure_airport=%s'
        cursor.execute(query,(datetime.today(), datetime.now().strftime("%H:%M:5S"), arrival, departure))
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

        data = executeSearchQuery(destination, source)
        if not data:
            flash("No flights found!", category='error')
            return redirect(url_for('views.home'))
        urls = [f'purchase_flight/'+str(flight['flight_number']) for flight in data]
        return render_template('home.html', user=session, data=zip(data, urls))

    return render_template('home.html', user=session, data=None)


@views.route('/view_flights', methods=['GET'])
def view_flights():
    if session['user'] and session['customerOrStaff'] == 'customer':
        cursor = conn.cursor()
        query = 'SELECT DISTINCT flight_number, flight_status, arrival_airport, departure_airport, ticket_id FROM tickets NATURAL JOIN flights NATURAL JOIN departs WHERE email = %s and %s < date and %s < time'
        cursor.execute(query, (session['user'], datetime.today(), datetime.now().strftime("%H:%M:%S")))
        data = cursor.fetchall()
        if not data:
            flash("No flights found!", category='error')
            return redirect(url_for('views.home'))
        cursor.close()
        urls = [f'flight_info/'+str(flight['ticket_id']) for flight in data]
        for flight in data:
            del flight['ticket_id']
        print(data)
        return render_template('view_flights.html', user=session, flights=zip(data, urls))
    return redirect(url_for('views.home'))


@views.route('/flight_info/<ticket_id>', methods=['GET', 'POST'])
def cancel_flight(ticket_id):
    if session['user'] and session['customerOrStaff'] == 'customer':
        cursor = conn.cursor()
        query = 'SELECT DISTINCT flight_number, flight_status, arrival_airport, departure_airport, ticket_id FROM tickets NATURAL JOIN flights WHERE ticket_id = %s'
        cursor.execute(query, (ticket_id))
        data = cursor.fetchone()
        flight_number = data['flight_number']
        departure_airport = data['departure_airport']
        cursor.close()
        if request.method=="POST":
            if "go_back" in request.form:
                return redirect(url_for('views.home'))
            if "cancel" in request.form:
                cursor = conn.cursor()
                query = 'SELECT DISTINCT * FROM `departs` WHERE flight_number = %s and name = %s'
                cursor.execute(query, (flight_number, departure_airport))
                data = cursor.fetchone()
                date_time = str(data['date']) + ' ' + str(data['time'])
                date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
                if ((date_time) - datetime.now()).total_seconds() > 86400:
                    query = 'DELETE FROM `tickets` WHERE ticket_id = %s'
                    cursor.execute(query, (ticket_id))
                    conn.commit()
                    flash("Successfully canceled flight!", category="success")
                else:
                    flash("Unable to cancel flight", category="error")
                cursor.close()
                return redirect(url_for('views.home'))
        del data['ticket_id']
        return render_template('flightInfo.html', flight=data)
    return redirect(url_for('views.home'))

@views.route('flight_info/rate_flight/<flight_number>', methods=['GET', 'POST'])
def rate_flight(flight_number):
    cursor = conn.cursor()
    query = 'SELECT DISTINCT * FROM arrives WHERE flight_number = %s'
    cursor.execute(query, (flight_number))
    data = cursor.fetchone()
    date_time = str(data['date']) + ' ' + str(data['time'])
    date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    cursor.close()
    if session['user'] and session['customerOrStaff'] == 'customer':
        if datetime.now() < date_time:
            flash("Can't rate flights you haven't flown yet", category="error")
        elif request.method == 'POST':
            rate = request.form.get("rate")
            comment = request.form.get("comment")
            cursor = conn.cursor()
            query = 'INSERT INTO rates VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (int(rate), comment, int(flight_number), session['user']))
            conn.commit()
            cursor.close()
            flash("Successfully reviewed flight!", category="success")
            return redirect(url_for('views.home'))
        return render_template('rateFlight.html')
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


@views.route('/trackSpending', methods=['GET', 'POST'])
def track_spending():
    if session['user'] and session['customerOrStaff'] == 'customer':
        cursor = conn.cursor()
        query = 'SELECT sold_price, date_time FROM tickets where date_time >= %s'
        one_year_ago = datetime.now() - relativedelta(years=1)
        cursor.execute(query, (one_year_ago))
        data = cursor.fetchall()
        if not data:
            flash("No tickets were bought in the last year", category='error')
            return redirect(url_for('views.home'))
        cursor.close()
        today = datetime.now()
        one_month_ago = datetime.now() - relativedelta(months=1)
        two_months_ago = datetime.now() - relativedelta(months=2)
        three_months_ago = datetime.now() - relativedelta(months=3)
        four_months_ago = datetime.now() - relativedelta(months=4)
        five_months_ago = datetime.now() - relativedelta(months=5)
        six_months_ago = datetime.now() - relativedelta(months=6)
        spent_this_year = 0
        spent_this_month = 0
        spent_one_month_ago = 0
        spent_two_months_ago = 0
        spent_three_months_ago = 0
        spent_four_months_ago = 0
        spent_five_months_ago = 0
        for sold_price, date_time in data:
            spent_this_year += sold_price
            if date_time > one_month_ago:
                spent_this_month += sold_price
            elif date_time > two_months_ago:
                spent_one_month_ago += sold_price
            elif date_time > three_months_ago:
                spent_two_months_ago += sold_price
            elif date_time > four_months_ago:
                spent_three_months_ago += sold_price
            elif date_time > five_months_ago:
                spent_four_months_ago += sold_price
            elif date_time > six_months_ago:
                spent_five_months_ago += sold_price
        track_this_year = "$" + str(spent_this_year)
        track_this_month = "$" + str(spent_this_month)
        track_one_month_ago = "$" + str(spent_one_month_ago)
        track_two_months_ago = "$" + str(spent_two_months_ago)
        track_three_months_ago = "$" + str(spent_three_months_ago)
        track_four_months_ago = "$" + str(spent_four_months_ago)
        track_five_months_ago = "$" + str(spent_five_months_ago)
        if request.method == "POST":
            start_date = request.form.get("start_date_range")
            end_date = request.form.get("end_date_range")
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            except:
                flash("start date range must be in the format of YYYY-MM-DD", category="error")
                return render_template('trackSpending.html')
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            except:
                flash("end date range must be in the format of YYYY-MM-DD", category="error")
                return render_template('trackSpending.html')
            if start_date > end_date:
                flash("start date cannot be after end date", category="error")
                return render_template('trackSpending.html')
            cursor = conn.cursor()
            query2 = 'SELECT sold_price FROM tickets where date_time > %s and date_time < %s'
            cursor.execute(query2, (start_date, end_date))
            data2 = cursor.fetchone()
            if not data:
                flash("No tickets were bought in the range selected", category='error')
                return redirect(url_for('views.home'))
            cursor.close()
            spent = 0
            for sold_price in data2:
                spent += sold_price
            track_spent = "$" + str(spent)
        # return render_template('trackSpending.html', data_1 = track_this_year, data_2 = track_spent)
        return render_template('trackSpending.html',
                                data_1=track_this_year,
                                month_1=track_this_month,
                                month_2=track_one_month_ago,
                                month_3=track_two_months_ago,
                                month_4=track_three_months_ago,
                                month_5=track_four_months_ago,
                                month_6=track_five_months_ago,
                                data_2 = track_spent)
    return redirect(url_for('views.home'))


####################################################################
#----------------------------STAFF CASES------------------------------

@views.route('/staff_manage_flights', methods=['GET', 'POST'])
def staff_manage_flights():
    if session['user'] and session['customerOrStaff'] == 'staff':
        if request.method == "POST":
            flight_number = request.form.get("flight_number")
            base_price = request.form.get("base_price")
            departure_airport = request.form.get("departure_airport")
            flight_status = request.form["status"]
            identification_number = request.form.get("identification_number")
            arrival_airport = request.form.get("arrival_airport")

            cursor = conn.cursor()
            query = "INSERT INTO `flights` VALUES (%s, %s, %s, %s, %s, %s)"
            print((int(flight_number), float(base_price), departure_airport, flight_status, int(identification_number), arrival_airport))
            cursor.execute(query, (int(flight_number), float(base_price), departure_airport, flight_status, int(identification_number), arrival_airport))
            conn.commit()
            cursor.close()

        # pass all flights of airline staff works for
        cursor = conn.cursor()
        query = 'SELECT DISTINCT * FROM flights WHERE flights.identification_number in (select identification_number from owns where name=%s);'
        cursor.execute(query, (session['staff_airline']))
        data = cursor.fetchall()
        if not data:
            flash("No flights found!", category='error')
            return redirect(url_for('views.home'))
        cursor.close()
        return render_template('staff_manage_flights.html', user=session, flights=data)


@views.route('/staff_manage_flights/change_flight_status/<flight_number>', methods=['GET', 'POST'])
def change_flight_status(flight_number):
    if request.method == "POST":
        flight_status = request.form["status"]

        cursor = conn.cursor()
        updateStatement = 'UPDATE FLIGHTS SET flight_status = %s WHERE flight_number=%s;'
        print(updateStatement)
        cursor.execute(updateStatement, (flight_status, flight_number))
        conn.commit()
        cursor.close()
        return redirect(url_for('views.staff_manage_flights'))
    cursor = conn.cursor()
    query = 'SELECT * FROM flights WHERE flight_number=%s'
    cursor.execute(query, flight_number)
    data = cursor.fetchone()
    return render_template('change_flight_status.html', user=session, flight=data)


@views.route('/staff_manage_airplane', methods=['GET', 'POST'])
def add_new_airplane():
    if session['user'] and session['customerOrStaff'] == 'staff':
        if request.method == "POST":
            identification_number = request.form.get("identification_number")
            num_of_seats = request.form.get("number_of_seats")
            manufacturing_company = request.form.get("manufacturing_company")
            age =request.form.get("age")

            cursor = conn.cursor()
            query = "INSERT INTO `airplanes` VALUES (%s, %s, %s, %s)"
            print((int(identification_number), int(num_of_seats), manufacturing_company, int(age)))
            cursor.execute(query,(int(identification_number), int(num_of_seats), manufacturing_company, int(age)))
            conn.commit()

            query= "INSERT INTO `owns` VALUES (%s, %s)"
            cursor.execute(query, (session["staff_airline"], identification_number))
            conn.commit()
            cursor.close()

        # pass all flights of airline staff works for
        cursor = conn.cursor()
        query = 'SELECT DISTINCT * FROM airplanes WHERE airplanes.identification_number IN (SELECT identification_number FROM owns WHERE name=%s);'
        cursor.execute(query, (session['staff_airline']))
        data = cursor.fetchall()
        if not data:
            flash("No Airlines found!", category='error')
        cursor.close()
        return render_template('staff_manage_airplane.html', user=session, airplanes=data)



@views.route('/staff_manage_airports', methods=['GET', 'POST'])
def staff_manage_new_airports():
    if session['user'] and session['customerOrStaff'] == 'staff':
        if request.method == "POST":
            name = request.form.get("name")
            city = request.form.get("city")
            airport_type = request.form["airport_type"]


            cursor = conn.cursor()
            query = "INSERT INTO `airports` VALUES (%s, %s, %s)"
            cursor.execute(query, (name, city, airport_type))
            conn.commit()

            # query = "INSERT INTO `owns` VALUES (%s, %s)"
            # cursor.execute(query, (session["staff_airline"], identification_number))
            # conn.commit()
            cursor.close()

        # pass all flights of airline staff works for
        cursor = conn.cursor()
        query = 'SELECT * FROM airports;'
        cursor.execute(query)
        data = cursor.fetchall()
        if not data:
            flash("No Airports found!", category='error')
        cursor.close()
        return render_template('staff_manage_airports.html', user=session, airports=data)


@views.route('/staff_view_flight_ratings', methods=['GET', 'POST'])
def staff_view_flight_ratings():
    if session['user'] and session['customerOrStaff'] == 'staff':
        flight_number = None
        data = None
        if request.method == "POST":
            flight_number = request.form.get("flight_number")

            cursor = conn.cursor()
            query = "SELECT * FROM RATES WHERE flight_number=%s"
            cursor.execute(query, flight_number)
            data = cursor.fetchall()
            if not data:
                flash("No Ratings Found!", category='error')
            cursor.close()

        return render_template('staff_view_flight_ratings.html', user=session, ratings=data)


@views.route('/staff_view_frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
    if session['user'] and session['customerOrStaff'] == 'staff':
        cursor = conn.cursor()
        query = 'SELECT email, COUNT(email) as tickets_bought FROM tickets WHERE YEAR(date_time) = YEAR(CURDATE()) GROUP BY 1 ORDER BY tickets_bought DESC LIMIT 1'
        cursor.execute(query)
        data = cursor.fetchone()
        cursor.close()
        if request.method == "POST":
            email = request.form.get('email')
            cursor = conn.cursor()
            query = 'SELECT * FROM flights WHERE flights.flight_number = (SELECT flights.flight_number FROM flights, tickets WHERE flights.flight_number = tickets.flight_number AND tickets.email = %s AND tickets.airline = (SELECT airline_name FROM staff WHERE %s = username))'
            cursor.execute(query, (email, session['user']))
            flights = cursor.fetchall()
            if not flights:
                flash("No flights found for this customer", category='error')
            else:
                return render_template('customerFlights.html', email=email, data=flights)
        return render_template('frequentCustomer.html', data=data)
    return redirect(url_for('views.home'))


@views.route('/staff_view_reports', methods=['GET', 'POST'])
def view_reports():
    return render_template('home.html', user=session, search=None)


@views.route('/view_revenue', methods=['GET', 'POST'])
def view_revenue():
    return render_template('home.html', user=session, search=None)