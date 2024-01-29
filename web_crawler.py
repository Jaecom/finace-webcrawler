import requests
from bs4 import BeautifulSoup
from srim import (
    findRoe,
    findControllingEquity,
    findExpectedReturn,
    findPrice,
    findNumberOfShares,
    calculateWeightedRoe,
    findName,
)
from prettytable import PrettyTable

rawCode = "069960"


code = f"A{rawCode}"
url = f"https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"
response = requests.get(url)

if response.status_code != 200:
    print("Failed to retrieve the web page")
    exit()

soup = BeautifulSoup(response.text, "html.parser")


roes = findRoe(soup)
weightedRoe = calculateWeightedRoe(
    [
        roes.get("roe-previous-y3"),
        roes.get("roe-previous-y2"),
        roes.get("roe-previous-y1"),
    ]
)

controllingEquity = findControllingEquity(soup).get("control-eq-previous-y1")
price = findPrice(soup)
shares = findNumberOfShares(soup, code)
name = findName(soup)
# expectedReturn = findExpectedReturn()
expectedReturn = 10.68

print("controllingEquity: ", controllingEquity)
print("weightedRoe: ", weightedRoe)
print("price: ", price)
print("shares: ", shares)
print("expectedReturn: ", expectedReturn)
print("")

excess_profit = (weightedRoe - expectedReturn) / 100 * controllingEquity


decreaseRatio = [1, 0.9, 0.8]

reasonable_stock_prices = [
    format(
        round(
            (
                controllingEquity
                + excess_profit * (ratio / (1 + expectedReturn / 100 - ratio))
            )
            / shares
        ),
        ",",
    )
    for ratio in decreaseRatio
]


table = PrettyTable()
table.field_names = [
    "주식이름",
    "가중 ROE",
    "기대수익률",
    "현재주가",
    "적정주가",
    "적정주가 (10% 감소)",
    "적정주가 (20% 감소)",
]

table.add_row(
    [
        name,
        weightedRoe,
        expectedReturn,
        format(price, ","),
        reasonable_stock_prices[0],
        reasonable_stock_prices[1],
        reasonable_stock_prices[2],
    ]
)

print(table)
