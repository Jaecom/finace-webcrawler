from srim import calculateSrimPrice
from prettytable import PrettyTable

rawCode = "069960"
srim = calculateSrimPrice(rawCode)

stockPriceLabels = [
    "적정주가" if ratio == 1 else f"적정주가 ({(round(1 - ratio, 1) * 100)}% 씩 감소)"
    for ratio in srim["decrease-ratios"]
]

table = PrettyTable()

table.field_names = [
    "주식이름",
    "가중 ROE",
    "기대수익률",
    "현재주가",
] + stockPriceLabels

table.add_row(
    [srim["name"], srim["weighted-roe"], srim["expected-return"], srim["price"]]
    + srim["stock-prices"]
)

print(table)
