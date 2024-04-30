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


def findExpectedReturn():
    url = "https://kisrating.com/ratingsStatistics/statics_spread.do"
    soup = getSoup(url)
    tds = soup.select(
        "div#con_tab1 tbody tr:has(td.fc_blue_dk:-soup-contains('BBB-')) td"
    )
    return float(tds[-1].text)
