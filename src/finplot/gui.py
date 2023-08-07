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
from settings import save_settings, get_preferred
from binance_api import start_kline_socket, supported_symbols
from plot import add_plot, update_plot

def create_intial_GUI():
    preferred_coins = get_preferred()
    for coin, tf in preferred_coins.items():
        add_plot(coin, tf)

    # Add control panel
    create_ctrl_panel(preferred_coins)

def create_ctrl_panel(preferred_coins: dict):
    """Creates the control panel at the bottom of the display."""
    ctrl_col = 0
    ctrl_row = 0

    for coin in preferred_coins:
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

        vars.timeframes.append(panel.timeframe)


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
    panel.asset.returnPressed.connect(change_selected_coin)
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
    panel.timeframe.currentTextChanged.connect(change_timeframe)
    panel.timeframe.setStyleSheet("background-color: white")
    layout.addWidget(panel.timeframe, ctrl_row, ctrl_col)


def add():
    """Adds a plot to the view."""
    add_plot("AXSUSDT", "15m")
    #vars.nr_charts += 1
    #update_plot("AXSUSDT", "15m")


def remove():
    """Removes a chart from the view."""
    vars.global_layout.itemAt(vars.widget_counter).widget().deleteLater()
    vars.global_layout.itemAt(vars.widget_counter + 1).widget().deleteLater()
    vars.widget_counter -= 2
    if vars.widget_counter + 1 % 4 == 0:
        vars.columns -= 1
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


def change_timeframe():
    """Handles the event of changing the timeframe."""
    counter = 0
    for tf in vars.timeframes:
        timeframe = tf.currentText()
        sym = vars.symbol_list[counter]

        if timeframe != vars.preferred[sym]:
            # Get ax of plot
            ax = vars.axs_dict[sym]
            ax[0].reset()
            ax[1].reset()

            vars.symbol_data_dict[sym] = pd.DataFrame()

            # Drop old plots
            vars.plots.pop(sym + " price")
            vars.plots.pop(sym + " volume")
            vars.plots.pop(sym + " rsi")

            # Get data for plot
            update_plot(sym, timeframe)

            vars.preferred[sym] = timeframe

            # Make a new websocket for this asset
            start_kline_socket(symbol=sym, interval=timeframe)

            fplt.refresh()

        counter += 1


def change_selected_coin():
    """Handles the event of changing the selected coin."""
    counter = 0
    for panel_coin in vars.selected_coins:
        selected_coin = panel_coin.text().upper()

        if vars.usdt_mode and input[-4:] != "USDT":
            selected_coin += "USDT"

        if (
            selected_coin in supported_symbols
            and selected_coin != vars.symbol_list[counter]
        ):
            # Get old symbol
            old_coin = vars.symbol_list[counter]

            # Get ax of plot and reset it
            ax = vars.axs_dict[old_coin]
            ax[0].reset()
            ax[1].reset()

            # Update symbol_dict
            vars.symbol_data_dict.pop(old_coin)
            vars.symbol_data_dict[selected_coin] = pd.DataFrame()

            # Change symbol_list
            vars.symbol_list[counter] = selected_coin

            vars.preferred.pop(old_coin)
            timeframe = vars.timeframes[counter].currentText()
            vars.preferred[selected_coin] = timeframe

            # Drop old plots
            vars.plots.pop(old_coin + " price")
            vars.plots.pop(old_coin + " volume")
            vars.plots.pop(old_coin + " rsi")

            # Get data for plot
            update_plot(selected_coin, timeframe)

            # Make a new websocket for this asset
            start_kline_socket(symbol=selected_coin, interval=timeframe)

            fplt.refresh()

        counter += 1
