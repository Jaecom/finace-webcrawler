from bs4 import BeautifulSoup
from util import getSoup
from typing import TypedDict


def calculateSrimPrice(rawCode: str, decreaseRatio: list[float], expectedReturn: float):
    code = f"A{rawCode}"
    url = f"https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"
    soup = getSoup(url)
    chart_soup = soup.select_one("div#highlight_D_A")

    row_type, roe, roe_current = findRoe(chart_soup)

    if roe < expectedReturn:
        return None

    controllingEquity = findControllingEquity(chart_soup)
    shares = calculateFloatingShares(chart_soup, code)
    price = findPrice(soup)
    name = findName(soup)
    per = findPER(soup)

    excess_profit = (roe - expectedReturn) / 100 * controllingEquity
    reasonable_stock_prices_list = [
        round(
            (
                controllingEquity
                + excess_profit * (ratio / (1 + expectedReturn / 100 - ratio))
            )
            / shares
        )
        for ratio in decreaseRatio
    ]

    return {
        "name": name,
        "roe": roe,
        "roe-type": row_type,
        "roe-current": roe_current,
        "expected-return": expectedReturn,
        "current-price": price,
        "expected-prices": reasonable_stock_prices_list,
        "decrease-ratios": decreaseRatio,
        "shares": shares,
        "per": per,
    }


def findName(soup: BeautifulSoup):
    return soup.select_one("div.ul_corpinfo h1#giName").text


def findPrice(soup: BeautifulSoup):
    span = soup.select_one("div.ul_3colgf li div span#svdMainChartTxt11")
    return convertInt(span.text)


def findPER(soup: BeautifulSoup):
    dd = soup.select_one("div#corp_group2 dl:has(a#h_per)> dd")
    return convertFloat(dd.text)


def findRoe(chart_soup: BeautifulSoup):
    tr = chart_soup.select_one('tr:has(a span.txt_acd:-soup-contains("ROE"))')
    td = tr.select("td.r")
    td_texts = [convertFloat(item.text) for item in td]

    roes = {
        "roe-previous-y3": td_texts[0],
        "roe-previous-y2": td_texts[1],
        "roe-previous-y1": td_texts[2],
        "roe-current-y": td_texts[3],
        "roe-current-q1": td_texts[4],
        "roe-current-q2": td_texts[5],
        "roe-current-q3": td_texts[6],
        "roe-current-q4": td_texts[7],
    }

    is_current = roes.get("roe-current-y") != 0

    roe_list = [
        roes.get("roe-previous-y3"),
        roes.get("roe-previous-y2"),
        roes.get("roe-previous-y1"),
    ]

    if is_current:
        roe_list = [
            roes.get("roe-previous-y2"),
            roes.get("roe-previous-y1"),
            roes.get("roe-current-y"),
        ]

    type, roe = calculateRoe(roe_list)

    return type, roe, is_current


def calculateRoe(roes: dict) -> tuple[str, float]:
    if roes[0] == roes[1] == roes[2]:
        return "N", roes[2]

    if (roes[0] < roes[1] < roes[2]) or (roes[0] > roes[1] > roes[2]):
        return "N", roes[2]

    weighted_row = round((roes[0] * 1 + roes[1] * 2 + roes[2] * 3) / 6, 2)
    return "W", weighted_row


def findControllingEquity(chart_soup: BeautifulSoup):
    tds = chart_soup.select('tr:has(div:-soup-contains("  지배주주지분")) td.r')
    equity_values = [convertInt(item.text) * 100000000 for item in tds]

    equity_list = {
        "control-eq-previous-y3": equity_values[0],
        "control-eq-previous-y2": equity_values[1],
        "control-eq-previous-y1": equity_values[2],
        "control-eq-current-y": equity_values[3],
        "control-eq-current_q1": equity_values[4],
        "control-eq-current_q2": equity_values[5],
        "control-eq-current_q3": equity_values[6],
        "control-eq-current_q4": equity_values[7],
    }

    return (
        equity_list["control-eq-current-y"]
        if equity_list["control-eq-current-y"] != 0
        else equity_list["control-eq-previous-y1"]
    )


def calculateFloatingShares(chart_soup: BeautifulSoup, code: str):
    tds = chart_soup.select('tr:has(div:-soup-contains("발행주식수")) td.r')
    totalShares = [convertInt(item.text) * 1000 for item in tds]
    companyOwnedShares = findCompanyOwnedShares(code)
    return totalShares[2] - companyOwnedShares


def findCompanyOwnedShares(code: str):
    url = f"https://comp.fnguide.com/SVO2/asp/SVD_shareanalysis.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=109&stkGb=701"
    soup = getSoup(url)
    tds = soup.select(
        'table#dataTable tr:has(div:-soup-contains("자기주식 (자사주+자사주신탁)")) td'
    )
    shares = convertInt(tds[1].text)
    return shares


def convertInt(text: str):
    str = text.replace(",", "")

    try:
        return int(str)
    except:
        return 0


def convertFloat(text: str):
    str = text.replace(",", "")

    try:
        return float(str)
    except:
        return 0
