import os
from math import pi

import pandas as pd
from bokeh.models import HoverTool
from bokeh.plotting import figure, show, gridplot, output_file, ColumnDataSource


def candle(ticker, days=365, zoom=20):
    PATH = os.path.join(os.getcwd() + './Stocks/' + ticker + ".csv")
    df = pd.read_csv(PATH).iloc[-days:]
    df["Date"] = pd.to_datetime(df["Date"])

    # Setting Axis
    max_high = df.iloc[-zoom:].High.max()
    min_low = df.iloc[-zoom:].Low.min()

    inc = df.Close > df.Open
    dec = df.Open > df.Close
    shift = df["18EMA"] < df["50EMA"]

    long_pivot = (df.Low < df.Low.shift(1)) & (df.Low < df.Low.shift(-1)) & (
            df.High.shift(-1) > df.High.shift(1)
    ) & (
                         df.High.shift(-2) > df.High.shift(1)
                 )

    long_reversal = (df.Open > df["18EMA"]) & (df.Close > df["18EMA"]) & (
            df.Low < df["18EMA"]
    ) & (
                            df.Low < df.Low.shift(1)
                    )
    w = 24 * 60 * 60 * 1000  # full day in ms

    sourceInc = ColumnDataSource.from_df(df.loc[inc])
    sourceDec = ColumnDataSource.from_df(df.loc[dec])
    hover = HoverTool(
        names=["dot"],
        tooltips=[
            ("open", "@Open"),
            ("close", "@Close"),
            ("high", "@High"),
            ("low", "@Low"),
            ("18EMA", "@18EMA"),
            ("50EMA", "@50EMA"),
            ("100EMA", "@100EMA"),
            ("200EMA", "@200EMA"),
        ],
    )
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(
        title=ticker,
        x_axis_type="datetime",
        tools=[TOOLS, hover],
        plot_width=475,
        plot_height=475,
        background_fill_color="white",
        y_range=(min_low - 5, max_high + 5),
        x_range=(df.iloc[-zoom].Date, df.iloc[-1].Date),
    )
    p.xaxis.major_label_overrides = {
        i: date.strftime("%b %d") for i, date in enumerate(pd.to_datetime(df["Date"]))
    }
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(df.Date, df.High, df.Date, df.Low, color="black")
    # p.vbar
    p.vbar(
        df.Date[inc],
        w,
        df.Open[inc],
        df.Close[inc],
        fill_color="green",
        line_color="black",
    )
    p.vbar(
        df.Date[dec],
        w,
        df.Open[dec],
        df.Close[dec],
        fill_color="red",
        line_color="black",
    )
    p.vbar(
        df.Date[shift],
        w,
        df.Open[shift],
        df.Close[shift],
        fill_color="purple",
        line_color="black",
    )
    p.vbar(
        df.Date[long_pivot],
        w,
        df.Open[long_pivot],
        df.Close[long_pivot],
        fill_color="orange",
        line_color="black",
    )
    p.vbar(
        df.Date[long_reversal],
        w,
        df.Open[long_reversal],
        df.Close[long_reversal],
        fill_color="blue",
        line_color="black",
    )
    p.line(df.Date, df["18EMA"], line_width=2, line_color="red")
    p.line(df.Date, df["50EMA"], line_width=2, line_color="green")
    p.line(df.Date, df["100EMA"], line_width=2, line_color="blue")
    p.line(df.Date, df["200EMA"], line_width=2, line_color="purple")

    p.circle("Date", "Close", name="dot", size=7, source=sourceDec, color="grey")
    p.circle("Date", "Close", name="dot", size=7, source=sourceInc, color="grey")

    return p


def DashBoard(list_of_plots, title):
    output_file(title + ".html", title=title)
    dash = []
    row = []
    iter = 0
    for i in list_of_plots:
        row.append(i)
        iter += 1
        if iter == 3:
            dash.append(row)
            row = []
            iter = 0
    dash.append(row)
    show(gridplot(dash))
