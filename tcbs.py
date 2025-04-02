# @title Hàm lấy dữ liệu bộ lọc (legacy)
from pandas import json_normalize
import json
import requests


tcbs_headers = {
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "DNT": "1",
    "Accept-language": "vi",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",  # noqa
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer": "https://tcinvest.tcbs.com.vn/",
    "sec-ch-ua-platform": '"Windows"',
}


def stock_screening_insights(
    params, size=2000, id=None, drop_lang="vi", headers=tcbs_headers
):
    """
    Get stock screening insights from TCBS Stock Screener
    Parameters:
        params (dict): a dictionary of parameters and their values for the stock screening.
        The keys should be the names of the filters, and the values should be either a single value or
            a tuple of two values (min and max) for the filter.
        For example:
            params = {
                "exchangeName": "HOSE,HNX,UPCOM",
                "epsGrowth1Year": (0, 1000000)
            }
        size (int): number of data points per page. Default is 2000 to get all data.
        id (str): ID of the stock screener. You can ignore this parameter.
        drop_lang (str): language of the column names to drop. Default is 'vi'.
        headers (dict): headers of the request. You can ignore this parameter.
    """
    url = "https://apipubaws.tcbs.com.vn/ligo/v1/watchlist/preview"

    # create a list of filters based on the params dictionary
    filters = []

    for key, value in params.items():
        # if the value is a tuple, it means it has a min and max value
        if isinstance(value, tuple):
            min_value, max_value = value
            filters.append({"key": key, "operator": ">=", "value": min_value})
            filters.append({"key": key, "operator": "<=", "value": max_value})
        # otherwise, it is a single value
        else:
            filters.append({"key": key, "value": value, "operator": "="})

    payload = {
        "tcbsID": id,
        "filters": filters,
    }
    if size is not None:
        payload["size"] = size

    # send request to get response
    response = requests.request(
        "POST",
        url,
        headers=headers,
        data=json.dumps(payload),
    ).json()

    df = json_normalize(response["searchData"]["pageContent"])

    # drop all columns has column name ended with `.vi`
    df = df[df.columns.drop(list(df.filter(regex=f"\.{drop_lang}$")))]

    # drop na columns
    df = df.dropna(axis=1, how="all")

    return df
