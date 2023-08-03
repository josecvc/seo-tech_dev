from keys import *
import utils, requests

def search_moby(query) -> bool:
    '''Searches the MobyGames database for games'''
    response = requests.get(f"https://api.mobygames.com/v1/games?title={utils.escape(query)}&api_key={os.environ['MOBY_KEY']}")

    data = response.json()
    
    if data["games"]: # if the search returns games
        print("Search results:")
        for game in data["games"]:
            # print(f"ID: {game['game_id']} Title: {game['title']}")
            print(game)
            
            # if game["description"]:
            #     print(game["description"])
            # else:
            #     print("No game description")
            
            # if game["genres"]:
            #     print("Genres:", ", ".join([genre["genre_name"] for genre in game["genres"]]))
            # else:
            #     print("No genres")
            
            # if game["platforms"]:
            #     print("Platforms:", ", ".join([plat["platform_name"] for plat in game["platforms"]]))
            # else:
            #     print("No platforms")
            
        return True
    else:
        print("No results")
        return False

if __name__ in "__main__":
    qu = input("Search (MobyGames): ")
    search_moby(qu)