# included modules
import random as rd
from urllib.request import urlopen

# third-party modules
from bs4 import BeautifulSoup

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
    page = urlopen("https://www.twitchquotes.com/random/feed")
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

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

# decorator for adding a tag to supplied function
def addTag(tag):
    # the wrapper func itself
    def wrapper(func):
        # add a tag attribute
        func.tag = tag
        return func
    # return wrapped function
    return wrapper