from flask import Flask, redirect, render_template, request, url_for, Response, jsonify ,make_response
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from datetime import datetime
from forms import *

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

# ----------- Foreign Relations

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
    games = db.relationship("Game", secondary=user_games, backref="games_played") # user plays games

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

    ratings = db.relationship("User", secondary=user_ratings, backref="user_ratings") # games have ratings
    genres = db.relationship("Genre", secondary=game_genres, backref="game_genres") # games have genres
    platforms = db.relationship("Platform", secondary=game_platforms, backref="game_platforms") # games have platforms
    
    
    def __repr__(self):
        return f"<Game>: {self.title}"

class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    rawgid = db.Column(db.Integer, nullable=False) # this is so I can update anything
    name = db.Column(db.String(30))

    def __repr__(self):
        return f"<Genre>: {self.genre}"

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
    desc = db.Column(db.Text)
    games = db.relationship("Game", secondary=collection_games, backref="collection_games") # games have platforms
    
    def __repr__(self):
        return f"<Collection>: {self.name}; User ID: {self.user_id}"
    
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

@app.route("/settings", methods=["GET", "POST"])
@login_required
def account_settings():
    return

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
    if not db.session.query(db.session.query(Game).filter_by(id=game_id).exists()).scalar(): # if the game is not in the database
        return render_template("e404.html"), 404
    game = Game.query.filter_by(id=game_id).one()
    return render_template("self_game.html", game=game)

@app.route("/user/<string:username>", methods=["POST", "GET"])
def user_page(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:    
        games_req = user_games.select().where(user_games.c.user_id == reqUser.id).order_by(user_games.c.last_played.desc())
        game_links = db.session.execute(games_req).fetchall()

        games = {}
        limit = 10
        '''
        GAME LINK
        (USER ID, GAME ID, HOURS, MINUTES, LAST_PLAYED)
        '''
        for link in game_links:
            print(link)
            if limit == 0:
                break
            the_game = Game.query.get(link[1])
            games[link[1]] = {
                "game_object": the_game,
                "hours_played": link[2],
                "minutes_played": link[3],
                "last_played": link[4]
            }
            limit -= 1
        return render_template("user_overview.html", user = reqUser, games=games) 

    
    
    return render_template("user_page.html", user = reqUser)

@app.route("/user/<string:username>/report", methods=["POST", "GET"])
def user_report(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        return render_template("user_page.html", user = reqUser)

@app.route("/user/<string:username>/library", methods=["POST", "GET"])
def user_library(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        return render_template("user_page.html", user = reqUser)

@app.route("/user/<string:username>/library", methods=["POST", "GET"])
def user_collections(username:str):
    try:
        reqUser = User.query.filter_by(username=username).one()
    except:
        return render_template("e404.html"), 404
    else:
        return render_template("user_page.html", user = reqUser)

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
       
async def get_games(session, url):
    '''Used to turn a game JSON into a Game object'''
    async with session.get(url) as resp:
        g_json = await resp.json()
        
        if "results" in g_json.keys():
            real_g = g_json["results"]
            ## then go through the list and convert into Game objects
            for game in real_g: # returns the value for each key
                genres = game["genres"] ## get genres, now we need to check which ones are in the database
                platforms = game["platforms"]

                data = await get_game(session, f"https://api.rawg.io/api/games/{game['id']}?key=b2c75793dd4744eda9a6ed86652c0b16") # get some additional information for the game

                if game["released"]:
                    releaseDate = datetime.strptime(game["released"], "%Y-%m-%d").date()
                else:
                    releaseDate = None

                if not db.session.query(db.session.query(Game).filter_by(title=game["name"]).exists()).scalar():
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
                    for fplatform in platforms:
                        platform = fplatform["platform"]
                        pName = platform["name"]
                        if not db.session.query(db.session.query(Platform).filter_by(name=pName).exists()).scalar(): # Add new platform if it does not exist
                            newPlat = Platform (  
                                rawgid = platform["id"],
                                name = platform["name"]
                            )
                            
                            db.session.add(newPlat)
                            db.session.commit()

                        currPlat = Platform.query.filter_by(name=pName).one() # get the platform and
                        g.platforms.append(currPlat) # add it to list of platform for game
                
                db.session.commit()


async def get_data(query:str="", pages:int = 3):
    '''Async retrieves game data from the API'''
    async with aiohttp.ClientSession() as session:
        games = []
        for i in range(1, pages+1):
            game_url = f"https://api.rawg.io/api/games?key=b2c75793dd4744eda9a6ed86652c0b16&search={utils.escape(query)}&page_size=50&page={i}"
             ## build up a collection of games

            games.append(asyncio.ensure_future(get_games(session, game_url)))

        # we can then insert this into the database

        await asyncio.gather(*games)

async def get_game(session, url): 
    '''This is just to async retrieve additional game information'''
    async with session.get(url) as response:
        return await response.json()