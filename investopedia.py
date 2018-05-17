from InvestopediaApi import ita
from bokeh.models import Span

from plotting import DashBoard, candle


def get_investopedia_position():
    uname = input("What is your investopedia username? ")
    passwd = input("Password? ")
    client = ita.Account(uname, passwd)
    portfolio = client.get_current_securities()
    dashboard = []
    for i in portfolio.bought:
        position = candle(i.symbol)
        if i.current_price > i.purchase_price:
            color = "green"
        else:
            color = "red"
        pur_price = Span(
            location=i.purchase_price,
            dimension="width",
            line_color=color,
            line_dash="dashed",
        )
        position.add_layout(pur_price)
        dashboard.append(position)
    DashBoard(dashboard, "Positions")
