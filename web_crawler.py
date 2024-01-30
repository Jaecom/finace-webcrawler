from srim import calculateSrimPrice
from prettytable import PrettyTable
import time

start_time = time.time()

expectedReturn = 10.68
decrease_ratio = [0.8, 0.9, 1]

stock_codes = [
    "005930",
    "373220",
    "000660",
    "207940",
    "035420",
    "051910",
    "005380",
    "006400",
    "035720",
    "000270",
    "005490",
    "105560",
    "096770",
    "068270",
    "028260",
    "055550",
    "012330",
    "323410",
    "034730",
    "066570",
    "015760",
    "010950",
    "086790",
    "259960",
    "032830",
    "003550",
    "017670",
    "033780",
    "377300",
    "009150",
    "018260",
    "316140",
    "010130",
    "051900",
    "003670",
    "036570",
    "030200",
    "000810",
    "302440",
    "352820",
    "090430",
    "024110",
    "361610",
    "086280",
    "011170",
    "251270",
    "009540",
    "326030",
    "034220",
    "018880",
]

stock_price_labels = [
    "적정주가" if ratio == 1 else f"적정주가 ({(round(1 - ratio, 1) * 100)}% 씩 감소)"
    for ratio in decrease_ratio
]

table = PrettyTable()

table.field_names = [
    "코드",
    "주식이름",
    "ROE",
    "기대수익률",
    "현재주가",
] + stock_price_labels

for code in stock_codes:
    srim = calculateSrimPrice(code, decrease_ratio, expectedReturn)

    if srim is None:
        continue

    table.add_row(
        [
            code,
            srim["name"],
            str(srim["roe"]) + "(W)" if srim["roe-type"] == "W" else srim["roe"],
            srim["expected-return"],
            srim["price"],
        ]
        + srim["stock-prices"]
    )

print(table)


end_time = time.time()
execution_time = end_time - start_time

print("Execution time:", execution_time, "seconds")
