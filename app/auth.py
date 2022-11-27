from flask import Blueprint, render_template, request, flash, redirect, url_for, session
# from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, conn
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import re

date_of_birth_regex = "^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"
auth = Blueprint('auth', __name__)


@auth.route('/customer-login', methods=['GET', 'POST'])
def customerLogin():
    if request.method =="POST":
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = conn.cursor()
        query = 'SELECT * FROM customers WHERE email = %s and user_password = %s'
        print(query)
        cursor.execute(query, (email, password))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            flash('Logged in successfully!', category='success')
            session['user'] = email
            session['customerOrStaff'] = 'customer'
            return redirect(url_for('views.home'))
        else:
            flash('Email does not exist.', category='error')
    return render_template('customerLogin.html', user=current_user)
    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     password = request.form.get('password')

    #     user = User.query.filter_by(email=email).first()
    #     if user:
    #         if check_password_hash(user.password, password):
    #             flash('Logged in successfully!', category='success')
    #             login_user(user, remember=True)
    #             return redirect(url_for('views.home'))
    #         else:
    #             flash('Incorrect password, try again!', category='error')
    #     else:
    #         flash('Email does not exist.', category='error')
    # return render_template('login.html', user=current_user)

@auth.route('staff-login', methods=["GET", "POST"])
def staffLogin():
    if request.method =="POST":
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = conn.cursor()
        query = 'SELECT * FROM staff WHERE username = %s and staff_password = %s'
        print(query)
        cursor.execute(query, (username, password))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            flash('Logged in successfully!', category='success')
            session['user'] = username
            session['customerOrStaff'] = 'staff'
            return redirect(url_for('views.home'))
        else:
            flash('Email does not exist.', category='error')
    return render_template('staffLogin.html', user=current_user)

@auth.route('/logout')
def logout():
    session['user'] = None
    session['customerOrStaff'] = None
    return redirect(url_for('views.home'))


@auth.route('/staff-sign-up', methods=['GET', 'POST'])
def staffSignUp():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        password = request.form.get('password').strip()
        date_of_birth = request.form.get('date_of_birth').strip()
        match = re.search(date_of_birth_regex, date_of_birth)
        print(date_of_birth)
        date_of_birth = date_of_birth.strip() + " 00:00:00"
        try:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d %H:%M:%S')
        except:
            flash("date_of_birth must be in the format of YYYY-MM-DD", category="error")
            return render_template('staffRegister.html', user=current_user)
        airline_name = request.form.get('airline_name').strip()
        cursor = conn.cursor()
        query = 'SELECT * FROM staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        query = 'SELECT * FROM airlines WHERE name = %s'
        cursor.execute(query, (airline_name))
        airline = cursor.fetchone()
        if(data):
            flash('Username already in use!', category='error')
        elif(len(first_name) < 2):
            flash('First name must be greater than 1 character.', category='error')
        elif(len(last_name) < 2):
            flash('Last name must be greater than 1 character.', category='error')
        elif(len(password) < 7):
            flash('Password must be at least 7 characters.', category='error')
        # elif(not match):
        #     flash('Please enter a valid date of birth in the year-month-day format!', category='error')
        elif(len(airline_name) < 2 or not airline):
            flash('Pleae enter a valid airline!', category='error')
        else:
            print("hello")
            cursor = conn.cursor()
            query = 'INSERT INTO `staff` (`username`, `staff_password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(query, (username, password, first_name, last_name, date_of_birth, airline_name))
            cursor.close()
            session['user'] = username
            session['customerOrStaff'] = 'staff'
            flash('Account Created!', category='success')
        # user = User.query.filter_by(email=email).first()
        # if user:
        #     flash('Email already exists!', category='error')
        # elif len(email) < 4:
        #     flash('Email must be greater than 3 characters.', category='error')
        # elif len(first_name) < 2:
        #     flash('First name must be greater than 1 character.', category='error')
        # elif password1 != password2:
        #     flash('Passwords don\'t match.', category='error')
        # elif len(password1) < 7:
        #     flash('Password must be at least 7 characters.', category='error')
        # else:
        #     # add new user to database
        #     new_user = User(email=email, first_name=first_name,
        #                     password=generate_password_hash(password1, method='sha256'))
        #     db.session.add(new_user)
        #     db.session.commit()
        #     login_user(new_user, remember=True)
        #     flash('Account Created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('staffRegister.html', user=current_user)