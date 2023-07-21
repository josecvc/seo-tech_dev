import requests
import urllib.parse
from keys import *


def escape(text:str) -> str:
    '''Escapes text to use for searching'''
    return urllib.parse.quote(text, safe='')

def search_moby(query) -> bool:

    response = requests.get(f"https://api.mobygames.com/v1/games?title={escape(query)}&api_key={os.environ['MOBY_KEY']}")

    data = response.json()

    if data["games"]: # if the search returns games
        for game in data["games"]:
            if game["title"]:
                print(game["title"] + "\n")
            else:
                print("No game title")
            
            if game["description"]:
                print(game["description"])
            else:
                print("No game description")
            
            if game["genres"]:
                print("Genres:", ", ".join([genre["genre_name"] for genre in game["genres"]]))
            else:
                print("No genres")
            
            if game["platforms"]:
                print("Platforms:", ", ".join([plat["platform_name"] for plat in game["platforms"]]))
            else:
                print("No platforms")
            
            return True
    else:
        return False
    
'''
APIs
- https://rawg.io/apidocs (I could use this to show popular games along with critic scores)
- https://www.igdb.com/api (Same as top)
- https://www.mobygames.com/info/api/ (Pretty much a datadump for videogames)
- https://partner.steamgames.com/doc/store/getreviews (User reviews verified by Steam)
- https://developer.valvesoftware.com/wiki/Steam_Web_API (Steam integration for importing games, and showing currently played games)
- 
'''

# if __name__ in "__main__":
#     query = input("Enter a game title: ")
#     search(query)
