import requests
from bs4 import BeautifulSoup


session = requests.Session()


def getSoup(url):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        return soup
    except requests.RequestException as e:
        print("Error fetching URL:", e)
        return None
