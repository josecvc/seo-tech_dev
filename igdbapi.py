import requests as r
from keys import *
import utils

def search_igdb(query):

    AUTH_URL = "https://id.twitch.tv/oauth2/token"

    auth_response = r.post(AUTH_URL, {
        "grant_type":"client_credentials",
        "client_id": os.environ["IGDB_ID"],
        "client_secret": os.environ["IGDB_SECRET"]
    })

    auth_response_data = auth_response.json()

    token = auth_response_data["access_token"]

    header = {
        "Client-ID": os.environ["IGDB_ID"],
        "Authorization": f"Bearer {token}"
    }

    response = r.post('https://api.igdb.com/v4/games', **{'headers': header,'data': f'fields *; search "{query}";limit 500;'})

    data = response.json()

    if not data:
        return False
    else:
        print("Search results:")
        for game in data:
            print(game, "\n")
        return True
    
if __name__ in "__main__":
    qu = input("Search (IGDb): ")
    search_igdb(qu)