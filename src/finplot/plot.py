import finplot as fplt
import pandas as pd
from ta.momentum import RSIIndicator
import pyqtgraph as pg

from binance_api import client, start_kline_socket
import vars


def add_plot(symbol, tf):
    """Adds a plot to the screen"""
    # Make axis
    ax, ax_rsi = fplt.create_plot_widget(vars.window, rows=2, init_zoom_periods=100)

    # Hide y-axis of chart graph
    ax.hideAxis("bottom")

    # ax.vb.setBackgroundColor(None)
    ax_rsi.vb.setBackgroundColor(None)

    ax.showGrid(True, True)
    ax_rsi.showGrid(True, True)

    vars.window.axs.append(ax)
    vars.window.axs.append(ax_rsi)

    vars.axs_dict[symbol] = [ax, ax_rsi]

    # Add widgets to layout, top to bottom, left to right
    # addWidget (self, QWidget, row, column, rowSpan, columnSpan, Qt.Alignment alignment = 0)
    # 1 (rowSpan of ax) + 3 (rowSpan of ax_rsi) = 4, so that is the row of rsi plot widget
    vars.global_layout.addWidget(ax.ax_widget, vars.row, vars.col, 1, 1)
    vars.row += 4
    vars.global_layout.addWidget(ax_rsi.ax_widget, vars.row, vars.col, 3, 1)
    vars.row += 3

    vars.widget_counter += 2

    # After 11 reset the counter
    if vars.row > 11:
        vars.col += 1
        vars.row = 0

    start_kline_socket(symbol=symbol, interval=tf)
    update_plot(symbol, tf)

    # add_widgets(sym)


# Adds candles and volume
def update_plot(sym, timeframe):
    # Get the ax
    ax = vars.axs_dict[sym][0]
    ax_rsi = vars.axs_dict[sym][1]

    # Use latest 120 candles to fill up the plot
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
    vars.plots[sym + " price"] = fplt.candlestick_ochl(
        df[["Time", "Open", "Close", "High", "Low"]], ax=ax
    )

    # Add volume overlay
    vars.plots[sym + " volume"] = fplt.volume_ocv(
        df[["Time", "Open", "Close", "Volume"]], ax=ax.overlay()
    )

    df.set_index("Time", inplace=True)

    # RSI overlay
    vars.plots[sym + " rsi"] = fplt.plot(
        RSIIndicator(close=df["Close"]).rsi(), ax=ax_rsi, color="#47c9d9"
    )

    # Use symbol name as legend
    fplt.add_legend(sym, ax=ax)

    # Save the data for this coin in the dictionary
    vars.symbol_data_dict[sym] = df

    # Make elements that highlight the current price
    price_highlight(df, ax, ax_rsi)


def price_highlight(df, ax, ax_rsi):
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

    # pgColor = pg.mkColor(rec_color)

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

    # Hex as #RRGGBBAA + 1A is 10% opacity
    fplt.add_band(30, 70, color=pg.mkColor("#9c24ac1A"), ax=ax_rsi)


# Update the plots
def realtime_update_plot():
    """Called at regular intervals by a timer."""

    # If call is too early
    if all(df.empty for df in vars.symbol_data_dict.values()):
        return

    # first update all data, then graphics (for zoom rigidity)
    # key = 'sym volume'
    for key in vars.plots:
        sym = key.split()[0]
        df = vars.symbol_data_dict[sym]

        # Get correct ax, first is for the chart
        axs = vars.axs_dict[sym]
        ax = axs[0]
        ax_rsi = axs[1]

        if key.split()[1] == "price":
            # OCHL for some reason
            vars.plots[key].update_data(df[["Open", "Close", "High", "Low"]])

        if key.split()[1] == "volume":
            vars.plots[key].update_data(df[["Open", "Close", "Volume"]])

        if key.split()[1] == "rsi":
            rsi = RSIIndicator(close=df["Close"]).rsi()
            vars.plots[key].update_data(rsi)

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

        if "-" in vars.countdown:
            vars.countdown = "0:00:00"

        ax.text.setHtml(
            (
                '<b style="color:white; background-color:'
                + rec_color
                + '";>'
                + str(current_price)
                + '</b> <body style="color:white; background-color:'
                + rec_color
                + '";>'
                + vars.countdown
                + "</body>"
            )
        )
