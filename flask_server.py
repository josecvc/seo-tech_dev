from flask import Flask, redirect, render_template, request, url_for, Response, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_apscheduler import APScheduler

from datetime import datetime, timedelta

import requests
from forms import *
from keys import *

import os
import aiohttp
import asyncio
import utils

# Security Imports
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from markupsafe import escape


app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] =\
      "sqlite:///vgset.db"

## For testing purposes
# app.config["TESTING"] = True
# app.config["SQLALCHEMY_DATABASE_URI"] =\
#       "sqlite:///"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SCHEDULER_API_ENABLED"] = True

app.secret_key = "fjdkjfkJLdAKkKJD:FKLjkJFK"

# Make database
db = SQLAlchemy()
db.init_app(app)

# Make scheduler
scheduler = APScheduler()
scheduler.init_app(app)



# Login
login = LoginManager()
login.init_app(app)
login.login_view = "login"
login.session_protection = "disabled"

# Bootstrap
bootstrap=Bootstrap5(app)

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ----------- Foreign Relations

game_genres = db.Table("game_genres", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("genre_id", db.Integer, db.ForeignKey("genre.id")),
                        )

game_platforms = db.Table("game_platforms", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("platform_id", db.Integer, db.ForeignKey("platform.id")),
                        )

game_publishers = db.Table("game_publishers", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("publisher_id", db.Integer, db.ForeignKey("publisher.id")),
                        )

game_developers = db.Table("game_developers", 
                        db.Column("game_id", db.Integer, db.ForeignKey("game.id")),
                        db.Column("developer_id", db.Integer, db.ForeignKey("developer.id")),
                        )

collection_games = db.Table("collection_games", 
                            db.Column("collection_id", db.Integer, db.ForeignKey("collection.id")),
                            db.Column("game_id", db.Integer, db.ForeignKey("game.id"))         
                            )

# ---------------- Models
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(16))
    create_date = db.Column(db.DateTime)
    steam_id = db.Column(db.BigInteger) 
    def __repr__(self):
        return f"<User>: {self.username}"
    
class Game(db.Model):
    '''A Game model for the database'''
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key= True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text)
    image = db.Column(db.Text) # filename
    background = db.Column(db.Text) # filename
    metacritic = db.Column(db.Integer)
    released = db.Column(db.Date)
    website = db.Column(db.Text)

    genres = db.relationship("Genre", secondary=game_genres, backref="game_genres") # games have genres
    platforms = db.relationship("Platform", secondary=game_platforms, backref="game_platforms") # games have platforms
    publishers = db.relationship("Publisher", secondary=game_publishers, backref="game_publishers")
    developers = db.relationship("Developer", secondary=game_developers, backref="game_developers")
    
    def __repr__(self):
        return f"<Game>: {self.title}"

class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Genre>: {self.name}"

class Platform(db.Model):
    __tablename__ = "platform"

    id = db.Column(db.Integer, primary_key=True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Platform>: {self.name}"

class Publisher(db.Model):
    __tablename__ = "publisher"

    id = db.Column(db.Integer, primary_key=True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Publisher>: {self.name}"

class Developer(db.Model):
    __tablename__ = "developer"

    id = db.Column(db.Integer, primary_key=True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Developer>: {self.name}"

class Collection(db.Model):
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(30), nullable=False)
    public = db.Column(db.Boolean)
    desc = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    games = db.relationship("Game", secondary=collection_games, backref="collection_games") # games have platforms
    
    def __repr__(self):
        return f"<Collection>: {self.name}; User ID: {self.user_id}"

class Rating(db.Model):
    __tablename__ = "rating"
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))

    rating = db.Column("rating", db.Integer, nullable = False)
    timestamp = db.Column("timestamp", db.DateTime)
    review = db.Column("review", db.Text)

    user = db.relationship("User", backref="ratings")
    game = db.relationship("Game", backref="ratings")

    def __repr__(self):
        return f"<Rating {self.id}>: User ID: {self.user_id}; Game ID: {self.game_id}; Rating: {self.rating}"
    
class Frag(db.Model):
    __tablename__ = "frag"
    id = db.Column(db.Integer, primary_key = True) # the frag id
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))

    time_played = db.Column(db.BigInteger)
    last_played = db.Column(db.DateTime)
    is_currently_playing = db.Column(db.Boolean)
    temp_played = db.Column(db.BigInteger)

    user = db.relationship("User", backref="session")
    game = db.relationship("Game", backref="session")

    def __repr__(self):
        return f"<Frag {self.id}>: User ID: {self.user_id}; Game ID: {self.game_id}"
    
# ---------------------------- Scheduled Tasks
@scheduler.task("interval", id="steam_check_currently_playing", seconds=3600)
def steam_currently_playing():
    with scheduler.app.app_context():
        steam_users:list[User] = User.query.filter(User.steam_id.is_not(None)).all()
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API}&steamids=" + str({user.steam_id for user in steam_users})

        resp = requests.get(url)
        data = resp.json()

        players:dict = data["response"]["players"]

        for player in players:
            if player["personastate"] != "0" and player["communityvisibilitystate"] != 1 : # if player is online and you can see their profile
                try: # attempt to retrieve data about game
                    user = User.query.filter_by(steam_id=player["steamid"]).one()
                    """
                    For each player, we need to first figure out if they are playing a game using a try except block.

                    Then we need to get the game they are playing from the database, then query the database to see if they are playing a game already. 
                    
                    For playing games:
                    - Check for gameplay
                    - Get game name (if not privated)
                    - Check for any currently played games. Stop that session.
                    - Update that session.
                    - Create a new session and put it as currently playing
                    - Store a temporary variable in the database for a session to calculate the final timedelta
                    - Commit everything

                    If they are not playing a game:
                    - Go to the database.
                    - Find an active session.
                    - Mark it as inactive.
                    - If there is no active session, do nothing
                    """
                    
                    game_title = player["gameextrainfo"] ## this is the name of the game they are playing (most of them closely match to the games in the database since RAWG is reputable)
                    
                    last_frag = Frag.query.filter_by(user_id = user.id).order_by(Frag.last_played.desc()).first()

                    game = Game.query.filter_by(title=game_title).one()
                    if game.id != last_frag.game_id or (game.id == last_frag.game_id and last_frag.is_currently_playing == False): # If you are not playing a game, or the game ids arent the same
                        # get the time they've been playing
                        time_now = datetime.now()
                        url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API}&steamid={player['steamid']}&format=json"
                        
                        resp = requests.get(url)
                        data = resp.json()
                        last_games = data["response"]["games"]

                        last_game = {}
                        for g in last_games:
                            if g["name"] == game.title:
                                last_game = g
                        if not last_game:
                            last_game["playtime_2weeks"] = 0

                        user = User.query.filter_by(steam_id=player["steamid"]).one()

                        # create the frag
                        frag = Frag(
                            user_id = user.id,
                            game_id = game.id,
                            time_played = 0,
                            last_played = time_now,
                            is_currently_playing = True,
                            temp_played = last_game["playtime_2weeks"] * 60
                        )
                        db.session.add(frag)
                        db.session.commit()
                            
                except KeyError: # meaning that the user is not playing anything or they have their steam account privated
                    # go to database and check if a session is active
                    if db.session.query(db.session.query(Frag).filter_by(is_currently_playing=True).\
                                        filter_by(user_id=user.id).exists()).scalar(): # if an active session
                        
                        active_frag = Frag.query.filter_by(is_currently_playing=True).\
                            filter_by(user_id = user.id).one()

                        active_frag.is_currently_playing = False

                        
                        
                        # get the game again to make the time delta

                        url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API}&steamid={player['steamid']}&format=json"

                        resp = requests.get(url)
                        data = resp.json()
                        last_games = data["response"]["games"]
                        last_game = None
                        for g in last_games:
                            if g["name"] == active_frag.game.title:
                                last_game = g
                        active_frag.time_played = (last_game["playtime_2weeks"] * 60) - active_frag.temp_played

                        db.session.commit()
                    
scheduler.start() 

# ---------------------------- Auth Routes
@app.route("/test/")
def test():
    return jsonify(success=True)

@app.errorhandler(404)
def error404(e):
    '''Everything that doesn't exist/you're not supposed to go to is 404'''
    return render_template('e404.html'), 404

@app.route("/login/", methods=["POST", "GET"])
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
    return render_template("login.html", form=login_form)

@app.route("/logout", methods=["POST","GET"])
@login_required
def logout():
    logout_user() # just log them out.
    return redirect(url_for("login"))

@app.route("/register/", methods=["POST", "GET"])
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
            # login_user(requestedUser)
            return redirect(url_for("login"))

    return render_template("register.html", form=register_form)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def account_settings():
    return render_template("user_pages/account_settings.html")

# ------------ Main Routes

@app.route("/", methods=["POST", "GET"]) # default page, if not logged in you get redirected here if you try to go to a personalised homepage
def landing():
    if current_user.is_authenticated: # redirect logged in user
        return redirect(url_for("home"))
    return render_template("landing.html")


@app.route("/home/", methods=["POST", "GET"])
@login_required
def home():
    filter_seven = datetime.today() - timedelta(days = 7)
    filter_thirty = datetime.today() - timedelta(weeks=4)
    # retrieve all games played in the last 7 days

    frags_last_seven_days = Frag.query.filter(Frag.last_played >= filter_seven).filter(Frag.user_id == current_user.id).all()
    top_games_last_month = db.session.query(
        Game, db.func.count(Frag.game_id), db.func.sum(Frag.time_played)
        ).outerjoin(
        Frag, Frag.game_id==Game.id).filter(
        db.and_(Frag.last_played >= filter_thirty, Frag.user_id == current_user.id)).group_by(Frag.game_id).order_by(
        db.func.count(Frag.game_id).desc(), db.func.sum(Frag.time_played).desc()).all()
    
    user_collections = Collection.query.filter(Collection.updated >= filter_seven).filter(Collection.user_id == current_user.id).order_by(Collection.updated).limit(10).all()

    return render_template("home.html", recent_frags = frags_last_seven_days, top_frags = top_games_last_month, collections = user_collections)  

@app.route("/games/", methods=["POST", "GET"])
def games():
    ## this is going to be a series of queries...
    # newly released games
    # most popular games of current year
    # most popular games of all time
    # most trending games
    # popular genres
    filter_month = datetime.today() - timedelta(weeks=4)
    filter_12month = datetime.today() - timedelta(weeks=52)

    new_games = db.session.query(Game).filter(db.and_(Game.released >= filter_12month, Game.released <= datetime.today())).order_by(Game.released.desc()).all()
  
    top_games_month = db.session.query(Game, db.func.count(Frag.game_id), db.func.sum(Frag.time_played)).join(
        Frag, Frag.game_id == Game.id
    ).filter(Frag.last_played >= filter_month).order_by(
        db.func.count(Frag.game_id).desc(), db.func.sum(Frag.time_played).desc()).group_by(Game.id).limit(10).all() 

    top_genres_month = db.session.query(
            Genre, db.func.count(Frag.game_id), db.func.sum(Frag.time_played)
        ).join(Game.genres).join(Frag, Frag.game_id==Game.id).filter(Frag.last_played >= filter_month).group_by(Frag.game_id).order_by(
        db.func.count(Frag.game_id).desc(), db.func.sum(Frag.time_played).desc()).limit(15).all()
 
 
    return render_template("games.html", new_games = new_games, top_games_month = top_games_month, top_genres_month=top_genres_month)

@app.route("/games/<int:game_id>/", methods=["POST", "GET"]) 
def game_page(game_id:int):
    if not db.session.query(db.session.query(Game).filter_by(id=game_id).exists()).scalar(): # if the game is not in the database
        return render_template("e404.html"), 404
    game = Game.query.filter_by(id=game_id).one()

    rating_form = RatingForm(request.form)

    ratings = Rating.query.filter_by(game_id = game_id).all()
    collections = Collection.query.filter(Collection.games.any(id=game_id)).limit(10).all()
    
    real_collections = []

    for collection in collections:
        real_collections.append((collection, User.query.get(collection.user_id)))
    total_sessions = Frag.query.filter_by(game_id=game_id).all()

    if current_user.is_authenticated:
        ## we want to check how many times the user has played the game, and how many hours/minutes in total
        ## we can also show the total number of people who have played the game
        sessions = Frag.query.\
            filter_by(game_id=game_id).\
            filter_by(user_id=current_user.id).all()
        
        return render_template("self_game.html", game=game, rating_form=rating_form, ratings=ratings, collections = real_collections, self_frags = sessions, all_frags = total_sessions)
    
    return render_template("self_game.html", game=game, rating_form=rating_form, ratings=ratings, collections = real_collections, all_frags = total_sessions)

@app.route("/user/<string:username>/", methods=["POST", "GET"])
def user_page(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:    
        sessions = Frag.query.filter_by(user_id = reqUser.id).order_by(Frag.last_played.desc()).limit(10).all()
        return render_template("user_pages/user_overview.html", user = reqUser, sessions = sessions) 


@app.route("/user/<string:username>/report", methods=["POST", "GET"])
def user_report(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        
        filter_seven = datetime.today() - timedelta(days=7)
        """
        For ease we will always look at the last seven days.
        We can show the user their top games, top genres, top times to play, a graph of their playtime by date
        """
        top_games_past_week = db.session.query(
        Game, db.func.count(Frag.game_id), db.func.sum(Frag.time_played)
        ).outerjoin(
        Frag, Frag.game_id==Game.id).filter(
        db.and_(Frag.last_played >= filter_seven, Frag.user_id == reqUser.id)).group_by(Frag.game_id).order_by(
        db.func.count(Frag.game_id).desc(), db.func.sum(Frag.time_played).desc()).limit(5).all()

        top_genres_past_week = db.session.query(
            Genre, db.func.count(Frag.game_id), db.func.sum(Frag.time_played)
        ).join(Game.genres).join(Frag, Frag.game_id==Game.id).filter(Frag.user_id == reqUser.id).group_by(Frag.game_id).order_by(
        db.func.count(Frag.game_id).desc(), db.func.sum(Frag.time_played).desc()).limit(5).all()

        top_times = db.session.query(Frag.last_played).filter(db.and_(Frag.last_played >= filter_seven, Frag.user_id == reqUser.id)).order_by(Frag.last_played.asc()).all()

        top_times_to_play = db.session.query(Frag.last_played, db.func.count(Frag.last_played))

        return render_template("user_pages/user_report.html", user=reqUser, games = top_games_past_week, genres = top_genres_past_week) 

@app.route("/user/<string:username>/library", methods=["POST", "GET"])
def user_library(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        session_select = db.session.query(Frag).filter_by(user_id = reqUser.id).order_by(Frag.last_played.desc())
        sessions = db.paginate(session_select) 

        f_form = FragForm(request.form)
        s_form = GameForm(request.form)

        return render_template("user_pages/user_library.html", user = reqUser, sessions = sessions, frag_form = f_form, search_form = s_form)

@app.route("/user/<string:username>/collections/", methods=["POST", "GET"])
def user_collections(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        form:FlaskForm = CollectionForm(request.form)
        if current_user.is_authenticated:
            if form.validate_on_submit() and reqUser.id == current_user.id: ## create the collection and redirect
                timestamp = datetime.now()
                if form.collection_desc.data == "":
                    desc = None
                else:
                    desc = form.collection_desc.data

                newCollection = Collection(
                    user_id = current_user.id,
                    name = form.collection_name.data,
                    desc = desc,
                    public = form.collection_boolean.data,
                    created = timestamp,
                    updated = timestamp
                )
                
                db.session.add(newCollection)
                db.session.commit()

                return redirect(url_for("self_collection", username=current_user.username, collection_id=newCollection.id))
            
        collections = db.paginate(Collection.query.filter_by(user_id = reqUser.id))
        return render_template("user_pages/user_collections.html", user = reqUser, collections = collections, form=form)

@app.route("/user/<string:username>/ratings")
def user_ratings(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        user_ratings = Rating.query.filter_by(user_id=reqUser.id).all()
        return render_template("user_pages/user_ratings.html", user = reqUser, ratings=user_ratings)

@app.route("/user/<string:username>/collections/<int:collection_id>/", methods=["POST", "GET"])
def self_collection(username:str, collection_id:str):
    ## Each collection will have games which you can call with collection.games.
    try:
        reqUser = User.query.filter_by(username=username).one()
        collection = Collection.query.get(collection_id)
    except:
        return render_template("e404.html"), 404
    else:
        if collection.public or (current_user.is_authenticated and reqUser.id == current_user.id):
            form = GameForm(request.form)
            return render_template("user_pages/self_collection.html", user = reqUser, collection = collection, form=form)
        else:

            return render_template("e404.html"), 404

@app.route("/search", methods=["POST", "GET"])
async def search_results():
    '''This will be of the form of a query string, e.g. <domain>.<tld>/search?q=<query>'''
    ## this will be paginated
    # we first want to check the database, we will use normal search (wildcard)
    if request.args.get("q") is not None:
        query =  request.args.get("q")

        # first query the database and paginate since it is much faster than calling an api
        # if no such game exists from the query, then go to RAWG API using async request
        # get all games from the api request and add them to the database, then return the search
        # if no rawg games were returned, then we know we cannot find it
        if not db.session.query(
            db.session.query(Game).filter(Game.title.like(f'{query}%')).exists()
                                                 ).scalar():
            await get_data(query)
        results = db.paginate(Game.query.filter(Game.title.like(f'{query}%')))
        return render_template("search_results.html", results = results, query = query)
    else:
       return render_template("search_results.html", query=None)

@app.post("/addtocollection")
@login_required
def add_to_collection():
    requested = request.get_json()
    collection:Collection = Collection.query.get(int(requested["collection_id"]))
    game:Game = Game.query.get(int(requested["game_id"]))
    collection.games.append(game)
    db.session.commit()
    return Response(status=201)

@app.get("/suggestgames")
@login_required
def suggest_games():
    query = request.args["q"]
    filter = Game.query.filter(Game.title.contains(query)).limit(30).all()
    games = []
    for game in filter:
        games.append({
            "id": game.id,
            "title": game.title,
            "background": game.background,
        })
    return jsonify(games)

@app.post("/addfrag")
@login_required
def add_frag():
    '''
    {
        game_id: k,
        date_played: dd/mm/yyyy,
        time_played: h, m, s, (Must be at least 5 minutes and at most 10 hours)
        unit: s
    }
    '''
    frag = request.get_json()
    
    # make sure all ints are actual ints
    frag["time_played"] = int(frag["time_played"]) 

    if frag["unit"] == "Hours":
        frag["time_played"] *= 3600
    elif frag["unit"] == "Minutes":
        frag["time_played"] *= 60
    # create timestamp
    timestr = frag["datestamp"] + " " + frag["timestamp"]
    timestamp = datetime.strptime(timestr, "%Y-%m-%d %H:%M")
    
    new_frag = Frag(
        user_id = current_user.id, 
        game_id = int(frag["game_id"]),
        last_played = timestamp,
        time_played = frag["time_played"]
    )
    db.session.add(new_frag)
    db.session.commit()

    return Response(status=201)

@app.post("/addrating")
@login_required
def add_rating():
    rating_block = request.get_json()
    ## first check if the person has already reviewed the game
    if not db.session.query(db.session.query(Rating).filter_by(game_id=rating_block["game_id"]).\
                filter_by(user_id=current_user.id).exists()).scalar():
        
        new_rating = Rating(
            user_id = current_user.id,
            game_id = int(rating_block["game_id"]),
            rating = int(rating_block["rating"]),
            timestamp = datetime.now(),
            review = rating_block["review"]
        )
        db.session.add(new_rating)
        db.session.commit()
    else:
        rating_update = Rating.query.filter_by(game_id = rating_block["game_id"]).\
        filter_by(user_id=current_user.id).one()

        rating_update.rating = int(rating_block["rating"])
        rating_update.timestamp = datetime.now()
        rating_update.review = rating_block["review"]

        db.session.commit()

    return Response(status=201)

@app.route("/steam_login", methods=["GET", "POST"])
@login_required
def steam_ok(): 
    try:
        # add steam_id to user
        user_steam_id = int(request.args["openid.identity"].replace("https://steamcommunity.com/openid/id/", "")) # retrieve steam id
        current_user.steam_id = user_steam_id
        db.session.commit()
        ## redirect to settings page
        return redirect(url_for("account_settings"))
    except KeyError: 
        return render_template("e404.html"), 404

@app.route("/remove_app", methods=["GET", "POST"])
def remove_app():
    pass

async def get_games(session, url):
    '''Used to turn a game JSON into a Game object'''
    async with session.get(url) as resp:
        g_json = await resp.json()
        
        if "results" in g_json.keys():
            real_g = g_json["results"]
            ## then go through the list and convert into Game objects
            for game in real_g: # returns the value for each key
                if game["added"] <= 35 or "(itch)" in game["name"].lower(): # filter out fluff (lol)
                    break

                genres = game["genres"] ## get genres, now we need to check which ones are in the database
                platforms = game["platforms"]
                

                data = await get_game(session, f"https://api.rawg.io/api/games/{game['id']}?key={RAWG_KEY}") # get some additional information for the game

                if game["released"]:
                    releaseDate = datetime.strptime(game["released"], "%Y-%m-%d").date()
                else:
                    releaseDate = None

                publishers = data["publishers"]
                developers = data["developers"]

                if not db.session.query(db.session.query(Game).filter_by(title=game["name"]).exists()).scalar(): # if the game is not in the database 
                    newGame = Game(
                        rawgid = game["id"],
                        title = game["name"],
                        desc = data["description_raw"],
                        metacritic = game["metacritic"],
                        released = releaseDate,
                        background = game["background_image"],
                        website = data["website"]
                    )
                    db.session.add(newGame)
                    db.session.commit()

                g = Game.query.filter_by(title=game["name"]).one()

                # Check if the update date is different to the row's update date, so we can change anything if needed

                if genres:
                    for genre in genres:
                        grName = genre["name"]
                        if not db.session.query(db.session.query(Genre).filter_by(name=grName).exists()).scalar(): # Add new genre if it does not exist
                            newGenre = Genre (  
                                rawgid = genre["id"],
                                name = genre["name"]
                            )
                            
                            db.session.add(newGenre)
                            db.session.commit()

                        currGenre = Genre.query.filter_by(name=grName).one() # get the genre and
                        g.genres.append(currGenre) # add it to list of genres for game
                
                if platforms:
                    for platform in platforms:
                        p = platform["platform"]
                        pName = p["name"]
                        if not db.session.query(db.session.query(Platform).filter_by(name=pName).exists()).scalar(): # Add new platform if it does not exist
                            newPlat = Platform (  
                                rawgid = p["id"],
                                name = pName
                            )
                            
                            db.session.add(newPlat)
                            db.session.commit()

                        currPlat = Platform.query.filter_by(name=pName).one() # get the platforms and
                        g.platforms.append(currPlat) # add it to list of platforms for game
                if publishers:
                    for publisher in publishers:
                        pName = publisher["name"]
                        if not db.session.query(db.session.query(Publisher).filter_by(name=pName).exists()).scalar(): # Add new platform if it does not exist
                            newPub = Publisher (  
                                rawgid = publisher["id"],
                                name = publisher["name"]
                            )
                            
                            db.session.add(newPub)
                            db.session.commit()

                        currPub = Publisher.query.filter_by(name=pName).one() # get the platform and
                        g.publishers.append(currPub) # add it to list of platform for game
                
                if developers:
                    for developer in developers:
                        dName = developer["name"]
                        if not db.session.query(db.session.query(Developer).filter_by(name=dName).exists()).scalar(): # Add new developer if it does not exist
                            newDev = Developer (  
                                rawgid = developer["id"],
                                name = developer["name"]
                            )
                             
                            db.session.add(newDev)
                            db.session.commit()

                        currDev = Developer.query.filter_by(name=dName).one() # get the developer and
                        g.developers.append(currDev) # add it to list of developers for game

                db.session.commit()


async def get_data(query:str="", pages:int = 3):
    '''Async retrieves game data from the API'''
    async with aiohttp.ClientSession() as session:
        games = []
        for i in range(1, pages+1):
            game_url = f"https://api.rawg.io/api/games?key={RAWG_KEY}&search={utils.escape(query)}&page_size=50&page={i}"
             ## build up a collection of games

            games.append(asyncio.ensure_future(get_games(session, game_url)))

        # we can then insert this into the database

        await asyncio.gather(*games)

async def get_game(session, url):

    '''This is just to async retrieve additional game information'''
    async with session.get(url) as response:
        return await response.json()
    

