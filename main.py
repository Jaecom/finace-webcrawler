from srim import calculateSrimPrice
from prettytable import PrettyTable
from util import findExpectedReturn
from kospi_200_codes import kospi_stock_codes


# stock_codes = [
#     "000270",
# ]
# expectedReturn = findExpectedReturn()
expectedReturn = 10.53

decrease_ratio = [0.8, 1]

expected_price_labels = [
    "적정주가" if ratio == 1 else f"적정주가 ({(round(1 - ratio, 1) * 100)}% 씩 감소)"
    for ratio in decrease_ratio
]

table = PrettyTable()

table.field_names = [
    "코드",
    "주식이름",
    "분야",
    "ROE",
    "PER",
    "현재주가",
] + expected_price_labels

for code in kospi_stock_codes:
    srim = calculateSrimPrice(code, decrease_ratio, expectedReturn)

    if srim is None:
        continue

    (
        current_price,
        expected_prices,
        per,
        roe,
        roe_type,
        roe_current,
        roe_trend,
        industry,
        name,
    ) = (
        srim["current-price"],
        srim["expected-prices"],
        srim["per"],
        srim["roe"],
        srim["roe-type"],
        srim["roe-is-current"],
        srim["roe-trend"],
        srim["industry"],
        srim["name"],
    )

    ratio_threshold_index = decrease_ratio.index(1)

    if current_price > expected_prices[ratio_threshold_index]:
        continue

    if per > 10:
        continue

    expected_return_str = str(expectedReturn) + "%"
    roe_str = str(roe)
    roe_format_str = (
        roe_str
        + "%"
        + (" ↑" if roe_trend == "UP" else " ↓" if roe_trend == "DOWN" else "  ")
    )
    current_price_str = format(current_price, ",")
    expected_prices_str = [
        format(price, ",")
        + (f" ({str(round(current_price / price * 100))})%" if index == 0 else "")
        for index, price in enumerate(expected_prices)
    ]
    per_str = str(per)

    table.add_row(
        [
            code,
            name,
            industry,
            roe_format_str,
            per_str,
            current_price_str,
        ]
        + expected_prices_str
    )

print("기대 수익률(BBB-):", expected_return_str)
print(table)
