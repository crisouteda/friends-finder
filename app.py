from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, logging
#from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
#from wtforms.validators import InputRequired, Email, Length
import sqlite3
import os
#import db

main = Blueprint('main', __name__)
currentdirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "you-will-never-guess"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
db = SQLAlchemy(app)
sqlite = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(255))
  email = db.Column(db.String(255))
  password = db.Column(db.String(255))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/signup', methods = ["GET", "POST"])
def signup():
  if request.method == "POST":
    email = request.form['email']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    try:
      new_user = User(email=email, username = username, password=password)
      db.session.add(new_user)
      db.session.commit()
      login_user(user)
      return redirect(url_for('friends'))
    except:
      return render_template("error_signup.html")
  else:
    return render_template("signup.html")

@app.route('/login',methods=["GET", 'POST'])
def login():
  if request.method == "POST":
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email = email).first()
    if user:
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('friends'))
    else:
      return("invalid username and password")
  else:
    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
  logout_user()
  return render_template("logout.html")

class Friends(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable = False)
    name = db.Column(db.String(200), nullable= False)
    age = db.Column(db.Integer, nullable= False)
    category = db.Column(db.String(20), nullable= False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
#Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id


@app.route('/delete/<int:id>', methods = ["POST", "GET"])
@login_required
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/find')
    except:
        "There was a problem deleting"


@app.route('/update/<int:id>', methods = ["POST", "GET"])
@login_required
def update(id):
    friend_to_update = Friends.query.get_or_404(id)
    if request.method == "POST":
        friend_to_update.name = request.form['name']
        friend_to_update.age = request.form['age']
        friend_to_update.category = request.form['category']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            "There was a problem updating"
    else:
        return render_template("update.html", friend_to_update = friend_to_update)


@app.route('/friends', methods = ["POST", "GET"])
@login_required
def friends():
    title = "My friend list"
    if request.method == "POST":
        name = request.form['name']
        user_id = current_user.id
        age = request.form['age']
        category = request.form['category']
        friend = Friends(name = name, user_id = user_id ,age = age, category = category)
        try:
            db.session.add(friend)
            db.session.commit()
            return redirect('/find')
        except:
            return "there was an error adding your friend"

    else:
        friends = Friends.query.filter(Friends.user_id.like(current_user.id))
        return render_template("find.html", title = title, friends = friends)

@app.route('/find', methods = ["POST" , "GET"])
@login_required
def find():
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        friends = Friends.query.filter(Friends.name.like(search))
        return render_template("find.html", friends = friends)
    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template("find.html", friends = friends)

@app.route('/')
def home():
  return render_template('home.html')

@app.errorhandler(404) 
def not_found(e):
  return render_template("notfound.html") 

if __name__ == '__main__':
    app.run(debug = True)