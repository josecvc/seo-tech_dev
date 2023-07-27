import requests
import utils
from keys import *

## API functions
import mobyapi
import igdbapi

'''
APIs
- https://rawg.io/apidocs (I could use this to show popular games along with critic scores)
- https://www.igdb.com/api (Same as top)
- https://www.mobygames.com/info/api/ (Pretty much a datadump for videogames)
- https://partner.steamgames.com/doc/store/getreviews (User reviews verified by Steam)
- https://developer.valvesoftware.com/wiki/Steam_Web_API (Steam integration for importing games, and showing currently played games)
- https://dev.epicgames.com/docs/web-api-ref (Epic Games Integration for importing games, and showing currently played games)
'''

def search_games(query):
    ## must return a list of Game objects or JSONs
    pass



if __name__ in "__main__":
    text = input("Search: ")

    ## Check database for data

    ## If no results in database, go to first API

    
