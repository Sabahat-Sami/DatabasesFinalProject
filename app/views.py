from app import app, render_template, auth

@app.route("/")
def home():
    return "Hello World"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")