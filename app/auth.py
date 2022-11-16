from app import app, request, redirect, url_for

@app.route('/loginAuth', methods=['GET','POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']
    return redirect(url_for('home'))

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    username = request.form['username']
    password = request.form['password']
    return redirect(url_for('home'))