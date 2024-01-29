from bs4 import BeautifulSoup
from util import getSoup

decreaseRatio = [1, 0.9, 0.8, 0.5]


def calculateSrimPrice(rawCode: str):
    code = f"A{rawCode}"
    url = f"https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"
    soup = getSoup(url)

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
    shares = calculateFloatingShares(soup, code)
    name = findName(soup)
    # expectedReturn = findExpectedReturn()
    expectedReturn = 10.68

    excess_profit = (weightedRoe - expectedReturn) / 100 * controllingEquity
    reasonable_stock_prices_list = [
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

    return {
        "name": name,
        "weighted-roe": weightedRoe,
        "expected-return": expectedReturn,
        "price": format(price, ","),
        "stock-prices": reasonable_stock_prices_list,
        "decrease-ratios": decreaseRatio,
    }


def findName(soup: BeautifulSoup):
    return soup.find("h1", id="giName").text


def findPrice(soup: BeautifulSoup):
    span = soup.find("span", id="svdMainChartTxt11")
    return convertInt(span.text)


def findRoe(soup: BeautifulSoup):
    tr = soup.find("span", class_="txt_acd", string="ROE").find_parent("tr")
    td = tr.find_all("td", class_="r")
    td_texts = [convertFloat(item.text) for item in td]

    return {
        "roe-previous-y3": td_texts[0],
        "roe-previous-y2": td_texts[1],
        "roe-previous-y1": td_texts[2],
        "roe-current-y": td_texts[3],
        "roe-current-q1": td_texts[4],
        "roe-current-q2": td_texts[5],
        "roe-current-q3": td_texts[6],
        "roe-current-q4": td_texts[7],
    }


def calculateWeightedRoe(roes: dict):
    result = (roes[0] * 1 + roes[1] * 2 + roes[2] * 3) / 6
    return round(result, 2)


def findControllingEquity(soup: BeautifulSoup):
    tr = (
        soup.find("div", string="  지배주주지분").find_parent("tr").find_all("td", class_="r")
    )
    equity_values = [convertInt(item.text) * 100000000 for item in tr]

    return {
        "control-eq-previous-y3": equity_values[0],
        "control-eq-previous-y2": equity_values[1],
        "control-eq-previous-y1": equity_values[2],
        "control-eq-current-y": equity_values[3],
        "control-eq-current_q1": equity_values[4],
        "control-eq-current_q2": equity_values[5],
        "control-eq-current_q3": equity_values[6],
        "control-eq-current_q4": equity_values[7],
    }


def findExpectedReturn():
    url = "https://kisrating.com/ratingsStatistics/statics_spread.do"
    soup = getSoup(url)
    trs = (
        soup.find("tbody")
        .find("td", class_="fc_blue_dk", string="BBB-")
        .find_parent("tr")
    )
    td = trs.find_all("td")[-1]
    return float(td.text)


def calculateFloatingShares(soup: BeautifulSoup, code: str):
    tr = soup.find("div", string="발행주식수").find_parent("tr").find_all("td", class_="r")
    totalShares = [convertInt(item.text) * 1000 for item in tr]
    companyOwnedShares = findCompanyOwnedShares(code)
    return totalShares[2] - companyOwnedShares


def findCompanyOwnedShares(code: str):
    url = f"https://comp.fnguide.com/SVO2/asp/SVD_shareanalysis.asp?pGB=1&gicode={code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=109&stkGb=701"
    soup = getSoup(url)
    tds = soup.find("div", string="자기주식 (자사주+자사주신탁)").find_parent("tr").find_all("td")
    return convertInt(tds[1].text)


def convertInt(text: str):
    if text == "\xa0":
        return -1

    str = text.replace(",", "")
    return int(str)


def convertFloat(text: str):
    if text == "\xa0":
        return -1

    str = text.replace(",", "")
    return float(str)
