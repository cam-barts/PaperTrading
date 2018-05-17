# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 16:36:51 2017

@author: Cameron
"""
import datetime as dt
import os
import queue
import threading
import time

import bs4 as bs
import pandas_datareader.data as web
import requests
from pandas_datareader._utils import RemoteDataError
from requests.exceptions import ContentDecodingError

from plotting import DashBoard, candle

NUM_THREADS = 20
q = queue.Queue()
to_plot = []
error_tickers = []
beginning = time.time()


def save_sp500_tickers():
    resp = requests.get("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs.BeautifulSoup(resp.text, "html5lib")
    table = soup.find("table", {"class": "wikitable sortable"})
    tickers = []
    for row in table.findAll("tr")[1:]:
        ticker = row.findAll("td")[0].text
        if "." in ticker:
            ticker = ticker.replace(".", "-")
            print("REPLACED TICKER: " + str(ticker))
        tickers.append(ticker)
        q.put(ticker)


def get_csvs():
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        try:
            get_csv_from_ticker(item)
            print("Retrieved " + str(item) + " Successfully")
        except RemoteDataError:
            print("Error retrieving " + str(item))
            error_tickers.append(item)
        except ContentDecodingError:
            print("Error retrieving " + str(item))
            print("$$$$$$$$$$$$$$$$$$$It Skipped")
            error_tickers.append(item)
        except ValueError:
            pass
        q.task_done()


def get_csv_from_ticker(ticker):
    start = dt.datetime(2000, 1, 1)
    today = dt.date.today()
    df = web.DataReader(ticker, "yahoo", start, today)
    df["18EMA"] = df["Adj Close"].ewm(
        span=18, min_periods=0, adjust=True, ignore_na=False
    ).mean()
    df["50EMA"] = df["Adj Close"].ewm(
        span=50, min_periods=0, adjust=True, ignore_na=False
    ).mean()
    df["100EMA"] = df["Adj Close"].ewm(
        span=100, min_periods=0, adjust=True, ignore_na=False
    ).mean()
    df["200EMA"] = df["Adj Close"].ewm(
        span=200, min_periods=0, adjust=True, ignore_na=False
    ).mean()
    df.reset_index(inplace=True)
    # Analysis Stuff
    infan = (df["18EMA"] > df["50EMA"]) & (df["50EMA"] > df["100EMA"]) & (
        df["100EMA"] > df["200EMA"]
    )
    continuation = (
        (
            df.Date[infan].tail(1).astype("datetime64[ns]")
            >= dt.datetime.now() - dt.timedelta(days=1)
        ).bool()
    ) and (
        (
            df.Date[~infan].tail(1).astype("datetime64[ns]")
            >= dt.datetime.now() - dt.timedelta(days=2)
        ).bool()
    )
    if continuation:
        to_plot.append(ticker)
    # output
    name = os.path.join(os.getcwd() + './Stocks/' + str(ticker) + ".csv")
    df.to_csv(name)


def get_csvs_concurrent():
    get_csvs()
    q.join()


if __name__ == "__main__":
    save_sp500_tickers()
    attempts = 4
    while attempts > 0:
        errors = 0
        get_csvs_concurrent()
        if len(error_tickers) == 0:
            break
        else:
            while len(error_tickers) > 0:
                q.put(error_tickers.pop())
                errors += 1
            attempts -= 1
    print(to_plot)
    if len(to_plot) > 0:
        dash = []
        for i in to_plot:
            dash.append(candle(i))
        DashBoard(dash, "Research")
    # get_investopedia_position()
    end = time.time()
    print(end - beginning)
    print(str(errors) + " tickers with errors")
