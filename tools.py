# using asynchronous web requests for some of the tools might be a good idea for the future
# ...when I'll eventually understand them

# included modules
import random as rd
import requests
import os
import pickle
import io

# third-party modules
import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from colorthief import ColorThief

# env variables
load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")

# useless docstring/help attribute parser, for now
def format(func):
    # below is a template of how docstrings should be done
    # ...for this project at least
    """Format my functions' docstrings
    
    func: A function

    Usage::
        format(function_with_docstring)
    """
    
    # separate usage section immediately
    usage = func.help[func.help.index('Usage::'):]

    # get all lines into a list
    docstrr = list(map(lambda x: x.strip(), func.help.split("\n")))

    # fetch name and description
    name = func.name
    desc = docstrr[0]

    # get every argument (unless i forget to mention one in the docstring)
    # and put it in a dictionary, along with its description
    args = {}
    for line in docstrr[1:docstrr.index("Usage::")]:
        if line.replace(" ", ""):
            arg, info = line.split(":")
            args[arg] = info
    
    return name, desc, args, usage

# website scraper explicitely made for https://www.twitchquotes.com/random/feed
def fetchCopypasta():
    # fetch the page and parse it into a soup object (mmm, soup)
    html = requests.get("https://www.twitchquotes.com/random/feed")
    if html.status_code != 200:
        return None
    soup = BeautifulSoup(html.text, "html.parser")

    # get all article elements (that's how most, if not all copypastas are formatted on the website)
    articles = soup.find_all("article")

    # put their title and copypasta in a dictionary
    copypastas = {}
    for article in articles:
        # get title and copypasta itself
        title = article.find("h3", attrs={"class": "-title-inner-parent"})
        copypasta = article.find("span", attrs={"class": "-main-text"})
        # sometimes, the copypasta is in a weirder format (image, nsfw, contains emotes)
        # so we skip it...is this the perfect solution? no
        # do i care? no
        if copypasta == None or copypasta.string == None:
            continue
        copypastas[title.string.replace("\n", "").strip()] = copypasta.string
    
    return copypastas

# scrap the comic you get from https://c.xkcd.com/random/comic/
def fetchComic():
    # you know the drill
    html = requests.get("https://c.xkcd.com/random/comic/")
    if html.status_code != 200:
        return None
    
    soup = BeautifulSoup(html.text, "html.parser")

    # title, comic itself BUT also the hover description
    title = soup.find("div", attrs={"id": "ctitle"}).string
    comic = soup.find("div", attrs={"id": "comic"}).find("img")

    return title, "https:"+comic.attrs.get("src"), comic.attrs.get("title")

# decorator for adding a tag to supplied function
def addTag(tag):
    # the wrapper func itself
    def wrapper(func):
        # add a tag attribute
        func.tag = tag
        return func
    # return wrapped function
    return wrapper

# get weather data for a given location from openweathermap.org
# needs two requests because their in-built geocoding API is no longer maintained
def getWeather(location, units = "metric"):
    # request data from the geocoding API
    # limit is set to 1 but can go up to 5

    if location:
        raw = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={WEATHER_API}")

        if raw.status_code != 200 or (not raw.json()):
            return None
        
        # get dictionary from response, then latitude and longitude
        data = raw.json()[0]
        lat, lon = data["lat"], data["lon"]
    
    else:
        lat, lon = round(rd.uniform(-90, 90), 9), round(rd.uniform(-180, 180), 9)

    # second request, this time for weather itself
    raw = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API}&units={units}")

    if raw.status_code != 200:
        return None
    
    # get dictionary from response, then the rest of the data
    data = raw.json()

    return data["name"] if data["name"] else "Unknown Name", data["weather"][0], data["main"], data["wind"]

# handle song data
def handleSongs(spotify = None):
    # create file if not there
    if not os.path.isfile("songs.pkl"):
        with open("songs.pkl", "wb") as f:
            pickle.dump({}, f)
    
    # load data from the file
    with open("songs.pkl", "rb") as f:
        data = pickle.load(f)

    # return that data it if needed
    if not spotify:
        return data
    
    # otherwise, add a new song to the list
    else:
        if spotify.track_id not in data:
            with open("songs.pkl", "wb") as f:
                # get the accent color of the song's cover
                # file object: much easier and simpler than writing the file to disk and then deleting it
                img = io.BytesIO(requests.get(spotify.album_cover_url).content)

                # get the color we need
                r,g,b = ColorThief(img).get_color(quality=10)

                # put all this new data into the file
                data[spotify.track_id] = {
                    "album": spotify.album, 
                    "album_cover_url": spotify.album_cover_url, 
                    "artists": spotify.artists,
                    "color": discord.Colour.from_rgb(r,g,b).value,
                    "title": spotify.title,
                    "track_url": spotify.track_url
                    }
                
                pickle.dump(data, f)