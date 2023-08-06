# Third party libraries
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mplfinance as mpf
import numpy as np
from binance.client import Client

# Local dependencies
from BinanceData import fetchData
import keys

# IDEAS:
# Trend lines (https://github.com/matplotlib/mplfinance/blob/master/examples/using_lines.ipynb)
# Plot stop loss hlines
# Use futures account positions

# Save your API keys in keys.py
client = Client(keys.public_key, keys.private_key)

# Get current holdings and save in owned
owned = []

# Fill owned list
assets = (client.get_account()).get('balances')
for asset in assets:
    sym = asset.get('asset')
    available = float(asset.get('free')) + float(asset.get('locked'))
    # Have more than 0 available
    if available > 0.001 :
        if sym != 'USDT':
            symUSDT = sym + 'USDT' 
            try:
                # Keep tracks of assets worth more than $10 in USDT
                if available * float(client.get_symbol_ticker(symbol = symUSDT)['price']) > 10:
                    owned.append(symUSDT)
            except Exception as e: 
                #Print out all the error information
                print("Error adding: " + symUSDT)

# === Default list ===
# List to use when owned consists of less than 9 items
default = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "DOTUSDT", "BCHUSDT", "LTCUSDT"]

# Add the default coins to owned
for sym in default:
    if sym not in owned:
        owned.append(sym)

# =========================
# =====   PLOTTING    =====
# =========================

# === TRADINGVIEW STYLE ===
# https://github.com/matplotlib/mplfinance/blob/master/examples/styles.ipynb
mc = mpf.make_marketcolors(up='#2e7871',down='#e84752',inherit=True)

s  = mpf.make_mpf_style(
                        base_mpf_style='nightclouds',
                        y_on_right=True,
                        marketcolors=mc,facecolor='#131722',
                        edgecolor='#4a4e59',
                        figcolor='#131722',
                        gridstyle='solid',
                        gridcolor='#1d202b')

fig = mpf.figure(style=s,figsize=(20,8))

# === CREATE PLOTS ===
#https://github.com/matplotlib/mplfinance/blob/master/examples/external_axes.ipynb

axs = []

# 9 plots
for x in range(1,10):
    axs.append(fig.add_subplot(3,3,x))

#https://github.com/matplotlib/mplfinance/blob/master/examples/plot_customizations.ipynb
#https://stackoverflow.com/questions/60599812/how-can-i-customize-mplfinance-plot

# This function gets called every x ms
def animate():

    # Latest 100 candles
    i = 0

    for ax in axs:

        symbol = owned[i]

        data = fetchData(symbol, 1, '15m')[-100:]

        # Clear old plot
        ax.clear()

        # Set title of every plot
        ax.set_title(symbol)
        ax.yaxis.get_major_formatter().set_scientific(False)

        current_price = data['close'].iloc[-1]
        old_price = data['close'].iloc[-2]

        if current_price > old_price:
            color = 'green'
        if current_price == old_price:
            color = 'gray'
        if current_price < old_price:
            color = 'red'

        # Draw current price
        ax.text(101,
                current_price, 
                f"{np.format_float_positional(current_price)}", 
                color="white", 
                ha="left", 
                va="center", 
                bbox=dict(facecolor=color, alpha=0.5))

        if i > 5:
            mpf.plot(
                    data,
                    ax=ax,
                    volume=False, 
                    type='hollow_and_filled',
                    #Plot time on x-axis
                    datetime_format='%H:%M', 
                    ylabel='', 
                    tight_layout=True, 
                    # Price Line
                    hlines=dict(hlines=current_price,linestyle='dashed',linewidths=(1)),
                    )
        else:
            mpf.plot(
                    data,
                    ax=ax,
                    volume=False,
                    type='hollow_and_filled',
                    datetime_format='',
                    ylabel='', 
                    tight_layout=True, 
                    hlines=dict(hlines=current_price,linestyle='dashed',linewidths=(1)),
                    )

        i = i+1

# Update every 5 seconds (1 sec = 1000ms)
ani = FuncAnimation(fig, animate, interval=5000)

plt.show()