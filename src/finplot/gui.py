import pandas as pd
from PyQt6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QWidget,
    QLineEdit,
    QPushButton,
    QGridLayout,
)
import pyqtgraph as pg
import finplot as fplt

# Local
import vars
from settings import save_settings, set_preferred
from binance_api import start_kline_socket, supported_symbols
from plot import add_plot, update_plot


def create_intial_GUI():
    set_preferred()
    for coin, tf in vars.preferred.items():
        add_plot(coin, tf)

    # Add control panel
    create_ctrl_panel()


def create_ctrl_panel():
    """Creates the control panel at the bottom of the display."""
    ctrl_col = 0
    ctrl_row = 0

    for coin in vars.preferred:
        if ctrl_row == 0:
            panel = QWidget()
            vars.global_layout.addWidget(panel)
            layout = QGridLayout(panel)

        if ctrl_col == 0:
            _create_timeframe_combobox(panel, layout, ctrl_col)
            _create_USDTmode_checkbox(panel, layout, ctrl_col)
            ctrl_col += 1

            _create_add_button(panel, layout, ctrl_col)
            _create_remove_button(panel, layout, ctrl_col)
            ctrl_col += 1

            _create_save_button(panel, layout, ctrl_col)
            ctrl_col += 1

        _create_coin_edit(panel, layout, ctrl_row, ctrl_col, coin)
        ctrl_col += 1

        _create_coin_tf_combobox(panel, layout, ctrl_row, ctrl_col)
        ctrl_col -= 1
        ctrl_row += 1

        if ctrl_row > 1:
            ctrl_row = 0
            ctrl_col += 2


def _create_timeframe_combobox(panel, layout, col_count):
    """Creates a combobox for timeframes."""
    panel.all_timeframes = QComboBox(panel)
    timeframes = "1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M".split(",")
    for timeframe in timeframes:
        panel.all_timeframes.addItem(timeframe)
    panel.all_timeframes.setCurrentIndex(3)
    panel.all_timeframes.setMaximumWidth(100)
    panel.all_timeframes.currentTextChanged.connect(all_timeframes)
    panel.all_timeframes.setStyleSheet("background-color: white")
    layout.addWidget(panel.all_timeframes, 0, col_count)


def _create_USDTmode_checkbox(panel, layout, col_count):
    """Creates a checkbox for USDT mode."""
    panel.USDTmode = QCheckBox(panel)
    panel.USDTmode.setText("USDT mode")
    panel.USDTmode.setCheckState(pg.Qt.QtCore.Qt.CheckState.Unchecked)
    panel.USDTmode.toggled.connect(USDT_mode)
    panel.USDTmode.setStyleSheet("color: white")
    layout.addWidget(panel.USDTmode, 1, col_count)


def _create_add_button(panel, layout, col_count):
    """Creates a button to add charts."""
    panel.add = QPushButton(panel)
    panel.add.setText("+")
    panel.add.clicked.connect(add)
    panel.add.setMaximumWidth(30)
    panel.add.setStyleSheet("background-color: white")
    layout.addWidget(panel.add, 0, col_count)


def _create_remove_button(panel, layout, col_count):
    """Creates a button to remove charts."""
    panel.remove = QPushButton(panel)
    panel.remove.setText("-")
    panel.remove.clicked.connect(remove)
    panel.remove.setMaximumWidth(30)
    panel.remove.setStyleSheet("background-color: white")
    layout.addWidget(panel.remove, 1, col_count)


def _create_save_button(panel, layout, col_count):
    """Creates a button to save settings."""
    panel.save = QPushButton(panel)
    panel.save.setText("Save Settings")
    panel.save.clicked.connect(save_settings)
    panel.save.setMaximumWidth(100)
    panel.save.setStyleSheet("background-color: white")
    layout.addWidget(panel.save, 0, col_count)


def _create_coin_edit(panel, layout, ctrl_row, ctrl_col, symbol):
    """Creates a QLineEdit widget for coin input."""
    panel.asset = QLineEdit(panel)
    panel.asset.setMaximumWidth(100)
    panel.asset.setText(symbol)
    panel.asset.returnPressed.connect(change_plot_data)
    panel.asset.setStyleSheet("background-color: white")
    layout.addWidget(panel.asset, ctrl_row, ctrl_col)
    vars.selected_coins.append(panel.asset)


def _create_coin_tf_combobox(panel, layout, ctrl_row, ctrl_col):
    """Creates a combobox for coin timeframes."""
    panel.timeframe = QComboBox(panel)
    timeframes = "1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M".split(",")
    for timeframe in timeframes:
        panel.timeframe.addItem(timeframe)
    panel.timeframe.setCurrentIndex(3)
    panel.timeframe.setMaximumWidth(100)
    panel.timeframe.currentTextChanged.connect(change_plot_data)
    panel.timeframe.setStyleSheet("background-color: white")
    layout.addWidget(panel.timeframe, ctrl_row, ctrl_col)
    vars.timeframes.append(panel.timeframe)


def add():
    """Adds a plot to the view."""
    add_plot("AXSUSDT", "15m")
    # vars.nr_charts += 1
    # update_plot("AXSUSDT", "15m")


def remove():
    """Removes a chart from the view."""
    # Delete plot and RSI
    vars.global_layout.itemAt(vars.widget_counter).widget().deleteLater()
    vars.global_layout.itemAt(vars.widget_counter + 1).widget().deleteLater()
    vars.widget_counter -= 2
    if vars.widget_counter + 1 % 4 == 0:
        vars.col -= 1
    if vars.widget_counter == 8:
        vars.widget_counter = 7


def USDT_mode(on):
    """Toggles the USDT mode."""
    vars.usdt_mode = on


def all_timeframes(control_panel):
    """Sets all timeframes to the selected value."""
    index = control_panel.all_timeframes.currentIndex()
    for panel in vars.timeframes:
        panel.setCurrentIndex(index)


def change_plot_data():
    """Handles the event of changing the timeframe."""

    # Compare result with preferred
    for i, (coin, timeframe) in enumerate(zip(vars.selected_coins, vars.timeframes)):
        coin = coin.text().upper()
        timeframe = timeframe.currentText()

        if vars.usdt_mode and input[-4:] != "USDT":
            coin += "USDT"

        if (coin not in vars.preferred and coin in supported_symbols) or vars.preferred[
            coin
        ] != timeframe:
            # Get ax of plot
            if coin in vars.axs_dict:
                ax = vars.axs_dict[coin]
                ax[0].reset()
                ax[1].reset()

                # Drop old plots
                vars.plots.pop(coin + " price")
                vars.plots.pop(coin + " volume")
                vars.plots.pop(coin + " rsi")

            # If the coin was changed
            else:
                old_coin = list(vars.preferred.keys())[i]
                ax = vars.axs_dict[old_coin]
                ax[0].reset()
                ax[1].reset()

                # Transfer information to new coin
                vars.axs_dict[coin] = ax

                # Update symbol_dict
                vars.symbol_data_dict.pop(old_coin)
                vars.preferred.pop(old_coin)

                # Drop old plots
                vars.plots.pop(old_coin + " price")
                vars.plots.pop(old_coin + " volume")
                vars.plots.pop(old_coin + " rsi")

            # Clear symbol data
            vars.symbol_data_dict[coin] = pd.DataFrame()

            # Get data for plot
            update_plot(coin, timeframe)

            vars.preferred[coin] = timeframe

            # Make a new websocket for this asset
            start_kline_socket(symbol=coin, interval=timeframe)

            # Close old websocket

            fplt.refresh()
