from flask import Flask, redirect, render_template, request, url_for, Response, jsonify ,make_response
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from datetime import datetime
from forms import *

# Security Imports
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from markupsafe import escape

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] =\
      "sqlite:///vgset.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "fjdkjfkJLdAKkKJD:FKLjkJFK"

# Make database
db = SQLAlchemy()
db.init_app(app)

# Login
login = LoginManager()
login.init_app(app)
login.login_view = "login"
login.session_protection = "basic"

# Bootstrap
bootstrap=Bootstrap5(app)

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

user_games = db.Table("user_games", # since many users can play many games
                        db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("hours_played", db.Integer),
                        db.Column("minutes_played", db.Integer),
                        db.Column("last_played", db.DateTime)
                        )

user_ratings = db.Table("user_ratings", 
                        db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),

                        db.Column("rating", db.Integer),
                        db.Column("timestamp", db.DateTime),
                        db.Column("review", db.Text)
                        )

game_genres = db.Table("game_genres", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("genre_id", db.Integer, db.ForeignKey("genre.id")),
                        )

game_platforms = db.Table("game_platforms", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("platform_id", db.Integer, db.ForeignKey("platform.id")),
                        )

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(16))
    create_date = db.Column(db.DateTime)
    games = db.relationship("Game", secondary=user_games, backref="games_played") # user plays games

    def __repr__(self):
        return f"<User>: {self.username}"
    
class Game(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text)
    image = db.Column(db.Text) # filename
    background = db.Column(db.Text) # filename

    ratings = db.relationship("User", secondary=user_ratings, backref="user_ratings") # games have ratings
    genres = db.relationship("Genre", secondary=game_genres, backref="game_genres") # games have genres
    platforms = db.relationship("Platform", secondary=game_platforms, backref="game_platforms") # games have platforms

    def __repr__(self):
        return f"<Game>: {self.title}"

class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Genre>: {self.genre}"

class Platform(db.Model):
    __tablename__ = "platform"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Platform>: {self.name}"



# ---------------------------- Auth Routes

@app.errorhandler(404)
def error404(e):
    '''Everything that doesn't exist/you're not supposed to go to is 404'''
    return render_template('e404.html'), 404

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    login_form = LoginForm(request.form)

    if login_form.validate_on_submit():
        password = login_form.password.data
        if db.session.query(db.session.query(User).filter_by(username=login_form.username.data).exists()).scalar(): # If that username exists
            requestedUser = User.query.filter_by(username=login_form.username.data).one()
            if check_password_hash(requestedUser.password, password): # If it is the same password
                login_user(requestedUser) # log them in and redirect to homepage
                return redirect(url_for("home"))
            else:
                return Response(status=401)
    return render_template("login.html", form=login_form)

@app.route("/logout", methods=["POST","GET"])
@login_required
def logout():
    logout_user() # just log them out.
    return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    register_form = RegisterForm(request.form)

    if register_form.validate_on_submit():
        if not db.session.query(db.session.query(User).filter_by(username=register_form.username.data).exists()).scalar() and not db.session.query(db.session.query(User).filter_by(email=register_form.email.data).exists()).scalar(): # username AND email are unique
            hashed_password = generate_password_hash(register_form.password.data)
            newUser = User(
                username=register_form.username.data,
                email=register_form.email.data,
                password=hashed_password,
                create_date = datetime.now()
            )

            db.session.add(newUser)
            db.session.commit()

            requestedUser = User.query.filter_by(username=register_form.username.data).one()
            login_user(requestedUser)
            return redirect(url_for("home"))

    return render_template("register.html", form=register_form)

# ------------ Main Routes

@app.route("/", methods=["POST", "GET"]) # default page, if not logged in you get redirected here if you try to go to a personalised homepage
def landing():
    if current_user.is_authenticated: # redirect logged in user
        return redirect(url_for("home"))

    return render_template("landing.html")


@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    
    return render_template("home.html")

@app.route("/games", methods=["POST", "GET"])
def games():
    return render_template("games.html")

@app.route("/games/<int:game_id>", methods=["POST", "GET"])
def game_page(game_id:int):
    if not db.session.query(db.session.query(User).filter_by(id=game_id).exists()).scalar():
        return render_template("e404.html"), 404
    game = Game.query.filter_by(id=game_id)
    return render_template("game_page.html", game=game)

@app.route("/user/<string:username>", methods=["POST", "GET"])
def user_page(username:str):
    if not db.session.query(db.session.query(User).filter_by(username=username).exists()).scalar():
        return render_template("e404.html"), 404
    
    reqUser = User.query.filter_by(username=username).one()
    return render_template("user_page.html", user = reqUser)

@app.route("/search", methods=["POST", "GET"])
def search_results():
    '''This will be of the form of a query string, e.g. <domain>.<tld>/search?q=<query>'''
    return render_template()