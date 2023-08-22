from flask_server import *

from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.init_app(app)

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
# @scheduler.task("interval", id="update_database", seconds=604800)
# def update_db_rawg():
    

# scheduler.start()

