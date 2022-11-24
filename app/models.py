from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# ZONAY- IM JUST CREATING ONE USER MODEL THAT IS SHARED BY CUSTOMER AND EMPLOYEE. MIGHT FIX LATER OR ADD A CATAGORICAL
# COLUMN TO SPECIFY BUT THAT SOUNDS INEFFICIENT

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
