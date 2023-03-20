"""Financial Dashboard from Yahoo Finance"""
import math
import datetime as dt
from datetime import date

import numpy as np
import yfinance as yf

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import TextInput, Button, MultiChoice, DateRangeSlider
from bokeh.models.widgets import Div

OPTIONS = ["30 Day SMA", "100 Day SMA", "200 Day SMA", "Linear Regression Line"]


def load_data(ticker1, ticker2, ticker3, ticker4, start, end):
    """Load Data from Yahoo Finance"""
    data_ticker1 = yf.download(ticker1, start, end)
    data_ticker2 = yf.download(ticker2, start, end)
    data_ticker3 = yf.download(ticker3, start, end)
    data_ticker4 = yf.download(ticker4, start, end)
    return data_ticker1, data_ticker2, data_ticker3, data_ticker4


def plot_data(data, indicators, sync_axis=None):
    """Plot Data"""
    data_frame = data
    gain = data_frame.Close > data_frame.Open
    loss = data_frame.Open > data_frame.Close
    width = 12 * 60 * 60 * 1000
    if sync_axis is not None:
        plot = figure(x_axis_type="datetime",
                      tools="pan, wheel_zoom, box_zoom, reset, save",
                      x_range=sync_axis, sizing_mode='stretch_both', margin=(0, 20, 20, 0))
    else:
        plot = figure(x_axis_type="datetime", margin=(0, 20, 20, 0),
                      tools="pan, wheel_zoom, box_zoom, reset, save",
                      sizing_mode='stretch_both')

    plot.xaxis.major_label_orientation = math.pi / 4
    plot.grid.grid_line_alpha = 0.25

    plot.segment(data_frame.index, data_frame.High, data_frame.index, data_frame.Low, color="black")
    plot.vbar(data_frame.index[gain], width, data_frame.Open[gain], data_frame.Close[gain],
              fill_color="#007f3e", line_color="#007f3e")
    plot.vbar(data_frame.index[loss], width, data_frame.Open[loss], data_frame.Close[loss],
              fill_color="#ae0e23", line_color="#ae0e23")

    for indicator in indicators:
        if indicator == OPTIONS[0]:
            data_frame['SMA30'] = data_frame['Close'].rolling(30).mean()
            plot.line(data_frame.index, data_frame.SMA30, color='purple',
                      legend_label=OPTIONS[0])
        elif indicator == OPTIONS[1]:
            data_frame['SMA100'] = data_frame['Close'].rolling(100).mean()
            plot.line(data_frame.index, data_frame.SMA100, color='blue',
                      legend_label=OPTIONS[1])
        elif indicator == OPTIONS[2]:
            data_frame['SMA200'] = data_frame['Close'].rolling(200).mean()
            plot.line(data_frame.index, data_frame.SMA200, color='yellow',
                      legend_label=OPTIONS[2])
        elif indicator == OPTIONS[3]:
            par = np.polyfit(range(len(data_frame.index.values)),
                             data_frame.Close.values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_pred = [slope * i + intercept for i in range(len(data_frame.index.values))]
            plot.segment(data_frame.index[0], y_pred[0], data_frame.index[-1], y_pred[-1],
                         legend_label=OPTIONS[3], color='red')
    return plot


def on_button_click(ticker1, ticker2, ticker3, ticker4, start, end, indicators):
    """Button click handle"""
    start_formatted = dt.datetime.fromtimestamp(start / 1000).strftime("%Y-%m-%d")
    end_formatted = dt.datetime.fromtimestamp(end / 1000).strftime("%Y-%m-%d")
    try:
        data_frame_ticker1, data_frame_ticker2, data_frame_ticker3, data_frame_ticker4 = \
            load_data(ticker1, ticker2, ticker3, ticker4, start_formatted, end_formatted)
        plot_ticker1 = plot_data(data_frame_ticker1, indicators)
        plot_ticker2 = plot_data(data_frame_ticker2, indicators, sync_axis=plot_ticker1.x_range)
        plot_ticker3 = plot_data(data_frame_ticker3, indicators)
        plot_ticker4 = plot_data(data_frame_ticker4, indicators, sync_axis=plot_ticker3.x_range)
        curdoc().clear()
        curdoc().add_root(layout)
        title1 = Div(text=f"<h2>{ticker1}</h2>")
        title2 = Div(text=f"<h2>{ticker2}</h2>")
        title3 = Div(text=f"<h2>{ticker3}</h2>")
        title4 = Div(text=f"<h2>{ticker4}</h2>")
        curdoc().add_root(row(column(title1, plot_ticker1), column(title2, plot_ticker2)))
        curdoc().add_root(row(column(title3, plot_ticker3), column(title4, plot_ticker4)))
    except ValueError as error:
        error_message = f'Error: Ticker Name must be supplied. {error}.'
        error_div = Div(text=error_message, sizing_mode='stretch_both',
                        style={'color': 'red', 'background-color': 'white',
                               'border': '2px solid black', 'border-radius': '15px',
                               'padding': '10px'})
        curdoc().clear()
        curdoc().add_root(layout)
        curdoc().add_root(error_div)


title = Div(text="<h2>Financial Dashboard</h2>",
            style={'font-size': '18px', 'width': '100%', 'text-align': 'center'})
stock1_text = TextInput(title="Ticker 1",
                        placeholder='Enter Ticker Name (Example AAPL for Apple)')
stock2_text = TextInput(title="Ticker 2",
                        placeholder='Enter Ticker Name (Example TSLA for Tesla)')
stock3_text = TextInput(title="Ticker 3",
                        placeholder='Enter Ticker Name (Example GOOG for Google)')
stock4_text = TextInput(title="Ticker 4",
                        placeholder='Enter Ticker Name (Example META for Facebook)')
date_range_slider = DateRangeSlider(title='Date Range:',
                                    value=(date(2021, 1, 1),
                                    dt.datetime.now().strftime("%Y-%m-%d")),
                                    start=date(2020, 1, 1),
                                    end=dt.datetime.now().strftime("%Y-%m-%d"),
                                    sizing_mode='stretch_width')
indicator_choice = MultiChoice(title='Select Indicator(s):',
                               options=OPTIONS, sizing_mode='stretch_width')
load_button = Button(label="Load Data", button_type="primary")
load_button.on_click(lambda: on_button_click(stock1_text.value.upper(), stock2_text.value.upper(),
                                             stock3_text.value.upper(), stock4_text.value.upper(),
                                             date_range_slider.start, date_range_slider.end,
                                             indicator_choice.value))
row0 = row(stock1_text, stock2_text)
row1 = row(stock3_text, stock4_text)
row2 = row(date_range_slider)
row3 = row(indicator_choice)
layout = column(title, row0, row1, row2, row3, load_button)

curdoc().clear()
curdoc().add_root(layout)
