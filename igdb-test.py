import requests as r
from keys import *

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

response = r.post('https://api.igdb.com/v4/games', **{'headers': header,'data': 'fields *; search "lego";limit 500;'})

data = response.json()
# print(data)

if not data:
    print("No results")
else:
    for game in data:
        print(game["name"])
