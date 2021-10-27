import numpy as np
import pandas as pd
import time
import pickle
from os import path
from datetime import datetime
from ta.momentum import RSIIndicator
import finplot as fplt
import PyQt5.QtCore as QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QGraphicsView,
    QComboBox,
    QCheckBox,
    QWidget,
    QLineEdit,
    QPushButton,
    QSpacerItem,
)
from PyQt5.QtGui import QApplication, QGridLayout
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import ctypes

client = Client()
bm = BinanceSocketManager(client)

# fplt.plots created are stored here
plots = {}

# TradingView style
# https://github.com/highfestiva/finplot/wiki/Settings
fplt.foreground = "#7a7c85"
fplt.background = "#131722"
# Candles
fplt.candle_bull_color = "#2e7871"
# For hollow candles:
# fplt.candle_bull_body_color = fplt.background
# For filled candles:
fplt.candle_bull_body_color = fplt.candle_bull_color
fplt.candle_bear_color = "#e84752"
# Cross hair
fplt.cross_hair_color = "#5e6b78"
# Volume
fplt.volume_bull_color = "#265f5e"
fplt.volume_bear_color = "#7d303a"
fplt.volume_bull_body_color = fplt.volume_bull_color

# List of symbols
# Dictionary of the preffered symbols and timeframes
preferred = {}
nr_charts = 4

# Convert it to a list
symbol_list = []

# Keeps track of number of widgets on screen
widget_counter = 0

# Keeps track of current column of widgets
col = 0
row = 0

# Save data of symbols here
symbol_data_dict = dict.fromkeys(symbol_list, pd.DataFrame())

# Save ax and ax_rsi here
axs_dict = {}

countdown = ""


def add_plot(sym):
    """Adds a plot to the screen"""
    global axs_dict
    global widget_counter
    global col
    global row

    # Make axis
    ax, ax_rsi = fplt.create_plot_widget(win, rows=2, init_zoom_periods=100)

    # Hide y-axis of chart graph
    ax.hideAxis("bottom")

    # ax.vb.setBackgroundColor(None)
    ax_rsi.vb.setBackgroundColor(None)

    ax.showGrid(True, True)
    ax_rsi.showGrid(True, True)

    win.axs.append(ax)
    win.axs.append(ax_rsi)

    axs_dict[sym] = [ax, ax_rsi]

    # Add widgets to layout, top to bottom, left to right
    # addWidget (self, QWidget, row, column, rowSpan, columnSpan, Qt.Alignment alignment = 0)
    # 1 (rowSpan of ax) + 3 (rowSpan of ax_rsi) = 4, so that is the row of rsi plot widget
    global_layout.addWidget(ax.ax_widget, row, col, 1, 1)
    row += 4
    global_layout.addWidget(ax_rsi.ax_widget, row, col, 3, 1)
    row += 3

    widget_counter += 2

    # After 11 reset the counter
    if row > 11:
        col += 1
        row = 0

    # add_widgets(sym)


# Currently disabled!
def add_widgets(symbol):
    """Function to add default widgets for a chart"""

    global widget_counter

    row_count = 0
    col_count = 0

    for chart_nr in range(2):
        # Add asset and timeframe widget
        # Asset
        control_panel.asset = QLineEdit(panel)
        control_panel.asset.setMaximumWidth(100)
        symbol_list.append(symbol)
        control_panel.asset.setText(symbol)

        # Do function if enter key got pressed
        control_panel.asset.returnPressed.connect(change_asset)
        control_panel.asset.setStyleSheet("background-color: white")
        layout.addWidget(control_panel.asset, row_count + 14, col_count)

        # Timeframe right of asset, next column
        col_count += 1

        # Add to list
        assets.append(control_panel.asset)

        # Timeframe
        control_panel.timeframe = QComboBox(panel)
        [
            control_panel.timeframe.addItem(i)
            for i in "1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M".split(",")
        ]
        control_panel.timeframe.setCurrentIndex(3)
        control_panel.timeframe.setMaximumWidth(100)
        control_panel.timeframe.currentTextChanged.connect(change_timeframe)
        control_panel.timeframe.setStyleSheet("background-color: white")
        layout.addWidget(control_panel.timeframe, row_count + 14, col_count)

        # For next symbol, go one row lower
        row_count += 1
        col_count -= 1

        if row_count > 1:
            row_count = 0
            col_count += 2

        widget_counter += 2

        # preferred[symbol] = panel.timeframe.currentText()

        # Start websockets based on timeframe selection
        # bm.start_kline_socket(symbol, ws_response, interval=panel.timeframe.currentText())

        # timeframes.append(panel.timeframe)

        # Update the plots
        # update_plot(symbol, panel.timeframe.currentText())


# Adds candles and volume
def update_plot(sym, timeframe):
    global plots

    # Get the ax
    ax = axs_dict[sym][0]
    ax_rsi = axs_dict[sym][1]

    # Use latest 120 candles to fill up
    hist_candles = client.get_klines(symbol=sym, interval=timeframe, limit=120)

    df = pd.DataFrame(hist_candles)

    # Only the columns containt the OHLCV data
    df.drop(columns=[6, 7, 8, 9, 10, 11], axis=1, inplace=True)

    # OHLCV
    df = df.rename(
        columns={0: "Time", 1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume"}
    )

    # Convert time in ms to datetime
    df = df.astype(
        {
            "Time": "datetime64[ms]",
            "Open": float,
            "High": float,
            "Low": float,
            "Close": float,
            "Volume": float,
        }
    )

    # plot the candles
    candles = df[["Time", "Open", "Close", "High", "Low"]]
    plots[sym + " price"] = fplt.candlestick_ochl(candles, ax=ax)

    # Add volume overlay
    volumes = df[["Time", "Open", "Close", "Volume"]]
    plots[sym + " volume"] = fplt.volume_ocv(volumes, ax=ax.overlay())

    df.set_index("Time", inplace=True)

    rsi = RSIIndicator(close=df["Close"]).rsi()
    plots[sym + " rsi"] = fplt.plot(rsi, ax=ax_rsi, color="#47c9d9")

    global symbol_data_dict

    # Add df for this symbol
    symbol_data_dict[sym] = df

    # Use symbol name as legend
    fplt.add_legend(sym, ax=ax)

    # Make elements that highlight the current price
    price_highlight(sym, ax, ax_rsi)


def price_highlight(sym, ax, ax_rsi):

    global symbol_data_dict
    df = symbol_data_dict[sym]

    # Define color of price line
    current_price = df["Close"].iloc[-1]
    old_price = df["Close"].iloc[-2]

    # Define color of rectangle
    # Or save color of last candle in a dictionary [sym] = lastcol
    if current_price > old_price:
        rec_color = "#2e7871"
    if current_price == old_price:
        rec_color = "#4a4e59"
    if current_price < old_price:
        rec_color = "#e84752"

    pgColor = pg.mkColor(rec_color)

    # Add current price line
    ax.price_line = pg.InfiniteLine(
        angle=0,
        movable=False,
        pen=fplt._makepen(fplt.candle_bull_body_color, style="--"),
    )
    ax.price_line.setPos(current_price)
    # ax.price_line.pen.setColor(pgColor)
    ax.addItem(ax.price_line, ignoreBounds=True)

    # If current_price is longer than 7 numbers make the font smaller
    # https://pyqtgraph.readthedocs.io/en/latest/graphicsItems/textitem.html
    ax.text = pg.TextItem(
        html=(
            '<b style="color:white; background-color:'
            + rec_color
            + '";>'
            + str(current_price)
            + "</b>"
        ),
        anchor=(0, 0.5),
    )
    # Set text at last candle
    ax.text.setPos(len(df.index), current_price)
    ax.addItem(ax.text, ignoreBounds=True)

    # Add lines to RSI
    ax_rsi.line70 = pg.InfiniteLine(
        angle=0, movable=False, pen=fplt._makepen("#ffffff", style="--")
    )
    ax_rsi.line70.setPos(70)
    ax_rsi.addItem(ax_rsi.line70, ignoreBounds=True)

    ax_rsi.line30 = pg.InfiniteLine(
        angle=0, movable=False, pen=fplt._makepen("#ffffff", style="--")
    )
    ax_rsi.line30.setPos(30)
    ax_rsi.addItem(ax_rsi.line30, ignoreBounds=True)

    # Hex as #RRGGBBAA, 1A is 10% opacity
    fplt.add_band(30, 70, color=pg.mkColor("#9c24ac1A"), ax=ax_rsi)


# === Websocket interpreter ===
def ws_response(info):
    """Info consists of:
    "e": "kline",         // Event type
    "E": 123456789,       // Event time (current time)
    "s": "BNBBTC",        // Symbol
    "k": {
      "t": 123400000,     // Kline start time (17:00)
      "T": 123460000,     // Kline close time (17:15) if 15m is selected as timeframe
      "s": "BTCUSDT",     // Symbol
      "i": "1m",          // Interval
      "f": "100",         // First trade ID
      "L": "200",         // Last trade ID
      "o": "0.0010",      // Open price
      "c": "0.0020",      // Close price
      "h": "0.0025",      // High price
      "l": "0.0015",      // Low price
      "v": "1000",        // Base asset volume
      "n": 100,           // Number of trades
      "x": false,         // Is this kline closed?
      "q": "1.0000",      // Quote asset volume
    Source: https://docs.binance.org/api-reference/dex-api/ws-streams.html
    """

    try:

        global symbol_data_dict

        sym = info["s"]
        tf = info["k"]["i"]

        # Skip response if symbol is not in dict
        if sym not in symbol_data_dict:
            return

        if tf != preferred[sym]:
            return

        df = symbol_data_dict[sym]

        close = float(info["k"]["c"])
        high = float(info["k"]["h"])
        low = float(info["k"]["l"])
        volume = float(info["k"]["v"])

        # t is the timestamp in ms
        t = int(info["k"]["t"])

        # Use int(info['k']['T']) - current time to calculate time untill next candle
        global countdown
        d1 = int(info["k"]["T"])
        converted_d1 = datetime.fromtimestamp(round(d1 / 1000))
        current_time = datetime.now()
        td = converted_d1 - current_time
        countdown = str(td).split(".")[0]

        t0 = int(df.index[-2].timestamp()) * 1000
        t1 = int(df.index[-1].timestamp()) * 1000
        t2 = t1 + (t1 - t0)

        # Update line corresponding with symbol
        if t < t2:
            # update last candle
            i = df.index[-1]
            df.loc[i, "Close"] = close
            df.loc[i, "High"] = high
            df.loc[i, "Low"] = low
            # df.loc[i, 'High']   = max(df.loc[i, 'High'], high)
            # df.loc[i, 'Low']    = min(df.loc[i, 'Low'],  low)
            df.loc[i, "Volume"] = volume
        else:
            # Add it all together, OCHLV
            data = [t] + [float(info["k"]["o"])] + [close] + [high] + [low] + [volume]
            candle = pd.DataFrame(
                [data], columns="Time Open Close High Low Volume".split()
            ).astype({"Time": "datetime64[ms]"})
            candle.set_index("Time", inplace=True)
            df = df.append(candle)

        # Symbol_dict consists of all ohlcv data
        symbol_data_dict[sym] = df

    # Catch any exception
    except Exception as e:
        print("Error handling websocket response")
        print(e)


# Update the plots
def realtime_update_plot():
    """Called at regular intervals by a timer."""
    global symbol_data_dict
    global plots

    # If call is too early
    if all(df.empty for df in symbol_data_dict.values()):
        return

    # first update all data, then graphics (for zoom rigidity)
    # key = 'sym volume'
    for key in plots:
        sym = key.split()[0]
        df = symbol_data_dict[sym]

        # Get correct ax, first is for the chart
        axs = axs_dict[sym]
        ax = axs[0]
        ax_rsi = axs[1]

        if key.split()[1] == "price":
            # OCHL for some reason
            plots[key].update_data(df[["Open", "Close", "High", "Low"]])

        if key.split()[1] == "volume":
            plots[key].update_data(df[["Open", "Close", "Volume"]])

        if key.split()[1] == "rsi":
            rsi = RSIIndicator(close=df["Close"]).rsi()
            plots[key].update_data(rsi)

        current_price = df["Close"].iloc[-1]
        old_price = df["Close"].iloc[-2]

        if current_price > old_price:
            rec_color = "#2e7871"
        if current_price == old_price:
            rec_color = "#4a4e59"
        if current_price < old_price:
            rec_color = "#e84752"

        # Color of line
        ax.price_line.pen.setColor(pg.mkColor(rec_color))

        # Position of line
        ax.price_line.setPos(current_price)

        # Position of text
        ax.text.setPos(len(df.index), current_price)

        # Text value
        global countdown

        if "-" in countdown:
            countdown = "0:00:00"

        ax.text.setHtml(
            (
                '<b style="color:white; background-color:'
                + rec_color
                + '";>'
                + str(current_price)
                + '</b> <body style="color:white; background-color:'
                + rec_color
                + '";>'
                + countdown
                + "</body>"
            )
        )


def change_asset():
    """Gets called if timeframes or asset gets changed in control panel"""

    # Change the symbol_list
    global symbol_list
    global symbol_data_dict
    global preferred

    counter = 0
    for asset in assets:

        input = asset.text().upper()

        if usdt_mode and input[-4:] != "USDT":
            new_symbol = asset.text().upper() + "USDT"
        else:
            new_symbol = asset.text().upper()

        if new_symbol in supported_symbols and new_symbol != symbol_list[counter]:

            # Get old symbol
            old_symbol = symbol_list[counter]

            # Get ax of plot
            ax = axs_dict[old_symbol]

            # Update symbol_dict
            symbol_data_dict.pop(old_symbol)
            symbol_data_dict[new_symbol] = pd.DataFrame()

            # Change symbol_list
            symbol_list[counter] = new_symbol

            ax[0].reset()
            ax[1].reset()

            preferred.pop(old_symbol)
            timeframe = timeframes[counter].currentText()
            preferred[new_symbol] = timeframe

            # Drop old plots
            plots.pop(old_symbol + " price")
            plots.pop(old_symbol + " volume")
            plots.pop(old_symbol + " rsi")

            # Get data for plot
            update_plot(new_symbol, timeframe)

            # Make a new websocket for this asset
            bm.start_kline_socket(new_symbol, ws_response, interval=timeframe)

            fplt.refresh()

        counter += 1


def change_timeframe():
    global preferred

    counter = 0

    for tf in timeframes:
        timeframe = tf.currentText()
        sym = symbol_list[counter]

        if timeframe != preferred[sym]:

            # Get ax of plot
            ax = axs_dict[sym]

            ax[0].reset()
            ax[1].reset()

            symbol_data_dict[sym] = pd.DataFrame()

            # Drop old plots
            plots.pop(sym + " price")
            plots.pop(sym + " volume")
            plots.pop(sym + " rsi")

            # Get data for plot
            update_plot(sym, timeframe)

            preferred[sym] = timeframe

            # Make a new websocket for this asset
            bm.start_kline_socket(sym, ws_response, interval=timeframe)

            fplt.refresh()

        counter += 1


usdt_mode = False


def USDT_mode(on):
    global usdt_mode
    if on:
        usdt_mode = True
    else:
        usdt_mode = False


def all_timeframes():
    global timeframes

    index = control_panel.all_timeframes.currentIndex()

    for panel in timeframes:
        panel.setCurrentIndex(index)


def add():
    global nr_charts

    # Symbol = next in preffered that is not used

    add_plot("AXSUSDT")
    nr_charts += 1
    update_plot("AXSUSDT", '15m')


def remove():
    """Removes a chart from the view"""
    global widget_counter
    global columns

    global_layout.itemAt(widget_counter).widget().deleteLater()
    global_layout.itemAt(widget_counter + 1).widget().deleteLater()

    widget_counter -= 2

    # widgets gets counted starting from 0, so first 4 plots are 7 widgets
    if widget_counter + 1 % 4 == 0:
        columns -= 1

    if widget_counter == 8:
        widget_counter = 7


assets = []
timeframes = []
row_count = 0
col_count = 0

def create_ctrl_panel():
    """Creates the control panel at the bottom of the display"""
    # could use timeframes instead of tf_list
    global preferred
    global row_count
    global col_count
    global layout

    # addWidget(QWidget, row, column, rowSpan, columnSpan, Qt.Alignment alignment = 0)
    for symbol in symbol_list:

        # Add widgets below the columns
        if row_count == 0:
            # Add QWidget to global_layout
            panel = QWidget()
            global_layout.addWidget(panel)

            # Set QWidget as parent
            layout = QGridLayout(panel)

        if col_count == 0:
            # Combobox to change all timeframes at once
            panel.all_timeframes = QComboBox(panel)
            [
                panel.all_timeframes.addItem(i)
                for i in "1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M".split(",")
            ]
            panel.all_timeframes.setCurrentIndex(3)
            panel.all_timeframes.setMaximumWidth(100)
            panel.all_timeframes.currentTextChanged.connect(all_timeframes)
            panel.all_timeframes.setStyleSheet("background-color: white")
            layout.addWidget(panel.all_timeframes, 0, col_count)

            # Checkbox for USDT mode
            panel.USDTmode = QCheckBox(panel)
            panel.USDTmode.setText("USDT mode")
            panel.USDTmode.setCheckState(0)
            panel.USDTmode.toggled.connect(USDT_mode)
            panel.USDTmode.setStyleSheet("color: white")
            layout.addWidget(panel.USDTmode, 1, col_count)

            col_count += 1

            # Controls to remove and add charts
            panel.add = QPushButton(panel)
            panel.add.setText("+")
            panel.add.clicked.connect(add)
            panel.add.setMaximumWidth(30)
            panel.add.setStyleSheet("background-color: white")
            layout.addWidget(panel.add, 0, col_count)

            panel.remove = QPushButton(panel)
            panel.remove.setText("-")
            panel.remove.clicked.connect(remove)
            panel.remove.setMaximumWidth(30)
            panel.remove.setStyleSheet("background-color: white")
            layout.addWidget(panel.remove, 1, col_count)

            col_count += 1

            panel.save = QPushButton(panel)
            panel.save.setText("Save Settings")
            panel.save.clicked.connect(save_settings)
            panel.save.setMaximumWidth(100)
            panel.save.setStyleSheet("background-color: white")
            layout.addWidget(panel.save, 0, col_count)

            # Place for one more button
            col_count += 1

        # Asset
        panel.asset = QLineEdit(panel)
        panel.asset.setMaximumWidth(100)
        panel.asset.setText(symbol)

        # Do function if enter key got pressed
        panel.asset.returnPressed.connect(change_asset)
        panel.asset.setStyleSheet("background-color: white")
        layout.addWidget(panel.asset, row_count, col_count)

        col_count += 1

        # Add to list
        assets.append(panel.asset)

        # Timeframe
        panel.timeframe = QComboBox(panel)
        [
            panel.timeframe.addItem(i)
            for i in "1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M".split(",")
        ]
        panel.timeframe.setCurrentIndex(3)
        panel.timeframe.setMaximumWidth(100)
        panel.timeframe.currentTextChanged.connect(change_timeframe)
        panel.timeframe.setStyleSheet("background-color: white")
        layout.addWidget(panel.timeframe, row_count, col_count)

        col_count -= 1
        row_count += 1

        if row_count > 1:
            row_count = 0
            col_count += 2

            # Add QSpacerItem

        preferred[symbol] = panel.timeframe.currentText()

        # Start websockets based on timeframe selection
        bm.start_kline_socket(
            symbol, ws_response, interval=panel.timeframe.currentText()
        )

        timeframes.append(panel.timeframe)

        # Update the plots
        update_plot(symbol, panel.timeframe.currentText())

    return panel


# Gets preferred settings at start up
def get_preferred():
    global preferred
    global nr_charts
    global symbol_list

    file = "settings.pkl"

    if path.exists(file):
        print("Found settings")

        # Get preffered pickle
        with open(file, "rb") as handle:
            preferred = pickle.load(handle)

        nr_charts = len(preferred)
        nr_charts = 4  # Remove this if more charts look nicer
        symbol_list = list(preferred.keys())[:nr_charts]

        print(preferred)

    else:
        print("No settings found, using default")
        preferred = {
            "BTCUSDT": "15m",
            "ETHUSDT": "15m",
            "XRPUSDT": "15m",
            "BNBUSDT": "15m",
            "ADAUSDT": "15m",
            "DOGEUSDT": "15m",
            "ETCUSDT": "15m",
            "MATICUSDT": "15m",
        }
        symbol_list = list(preferred.keys())[:nr_charts]

    for sym in symbol_list:
        add_plot(sym)


# Do this if the save button is pressed
def save_settings():
    file = "settings.pkl"

    # Write currently prefferd as pickle
    with open(file, "wb") as handle:
        pickle.dump(preferred, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Saved settings")

if __name__ == "__main__":

    # Make PyQt5 related stuff
    app = QApplication([])
    win = QGraphicsView()
    # Layout for the charts
    global_layout = QGridLayout()
    win.setLayout(global_layout)
    win.setWindowTitle("Charts")

    # Get list of currently supported symbols
    supported_symbols = [d["symbol"] for d in client.get_exchange_info().get("symbols")]

    # Background color surrounding the plots
    win.setStyleSheet("background-color:" + fplt.background)
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    win.resize(width*0.9, height*0.7)

    # Finplot requres this property
    win.axs = []
    fplt.autoviewrestore()

    get_preferred()

    # Add control panel
    control_panel = create_ctrl_panel()

    # Start binance sockets
    bm.start()

    # Gets called every 5 sec
    fplt.timer_callback(realtime_update_plot, 5)

    # prepares plots when they're all set up
    fplt.show(qt_exec=False)
    win.show()
    app.exec_()

# Maybe use symbol + tf as key for axs_dict
# Fix deleting
# Decrease font size of price_highlight when new charts get added
# Adjust to different screen sizes
# Save control panel settings somewhere (assets and tf)
# Maybe save historical candles
# Caching??, see complicated.py
# Make updating RSI more efficient
# Fix candlestick countdown when different timeframes are selected, change global countdown
# Add s/r levels?
# $BTC.D chart, https://www.tradingview.com/symbols/CRYPTOCAP-BTC.D/
# $TOTAL chart, https://www.tradingview.com/symbols/CRYPTOCAP-TOTAL/
# Show funding percentage
# Show percentual difference of candle in crosshair, possible?? https://github.com/highfestiva/finplot/wiki/Snippets#custom-crosshair-and-legend

# Stock ideas, use yfinance lib:
# DXY chart?
# Add bid-ask chart?
# Heatmap of limit orders (bids) (instead of bid-ask chart) https://github.com/highfestiva/finplot/blob/master/finplot/examples/heatmap.py
# Add sound effect for quick price increase / decline
