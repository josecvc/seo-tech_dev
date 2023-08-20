from flask_server import *
import aiohttp
import asyncio
import utils
from datetime import datetime

async def get_games(session, url, db):
    '''Used to turn a game JSON into a Game object'''
    async with session.get(url) as resp:
        g_json = await resp.json()
        real_g = g_json["results"]
        ## then go through the list and convert into Game objects
        for game in real_g: # returns the value for each key
            genres = game["genres"] ## get genres, now we need to check which ones are in the database
            platforms = game["platforms"]

            data = await get_game(session, f"https://api.rawg.io/api/games/{game['id']}?key=b2c75793dd4744eda9a6ed86652c0b16") # get some additional information for the game
            # with app.app_context():
            if not db.session.query(db.session.query(Game).filter_by(title=game["name"]).exists()).scalar():
                newGame = Game(
                    rawgid = game["id"],
                    title = game["name"],
                    desc = data["description_raw"],
                    metacritic = game["metacritic"],
                    released = datetime.strptime(game["released"], "%Y-%m-%d").date(),
                    background = game["background_image"],
                    website = data["website"]
                )
                db.session.add(newGame)
                db.session.commit()

            g = Game.query.filter_by(title=game["name"]).one()

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


async def get_data(db, query:str="", pages:int = 3, ):
    '''Async retrieves game data from the API'''
    async with aiohttp.ClientSession() as session:
        games = []
        for i in range(1, pages+1):
            game_url = f"https://api.rawg.io/api/games?key=b2c75793dd4744eda9a6ed86652c0b16&search={utils.escape(query)}&page_size=50&page={i}"
             ## build up a collection of games

            games.append(asyncio.ensure_future(get_games(session, game_url, db)))

        # we can then insert this into the database

        paginated_games = await asyncio.gather(*games)

async def get_game(session, url): 
    '''This is just to async retrieve additional game information'''
    async with session.get(url) as response:
        return await response.json()

if __name__ in "__main__":
    asyncio.run(get_data())