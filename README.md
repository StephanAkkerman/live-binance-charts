# Live Binance Charts
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/github/license/StephanAkkerman/Live_Binance_Charts.svg?color=brightgreen)](https://opensource.org/licenses/MIT)

---
This repository showcases my efforts in visualizing live cryptocurrency price data from the Binance exchange using two distinct implementations.

## 📊 Implementations
### 1. finplot
Utilizing `finplot` combined with `PyQt6`, this implementation offers a sophisticated and advanced charting solution in Python.

### 2. mplfinance
Leveraging `mplfinance`—built on the foundation of the widely-used `matplotlib` library—this approach provides another way to chart cryptocurrency data. Configure your Binance API keys in `src/mplfinance/keys.py` to auto-plot your assets, or leave it blank to manually specify the cryptocurrencies you'd like to visualize.

## ✨ Features
- Dark Mode: Enjoy a Tradingview-style dark theme for better visual clarity.
- Customizable View: Easily add or remove charts as per your preferences.
- Real-time Updates: Stay updated with live data thanks to the Binance websocket integration.

## Dependencies
The required packages to run this code can be found in the `requirements.txt` file. To run this file, execute the following code block:
```
$ pip install -r requirements.txt 
```
Alternatively, you can install the required packages manually like this:
```
$ pip install <package>
```

## How to run
- Clone the repository
- Run `$ python src/finplot/main.py` or `$ python src/mplfinance/main.py` 
- See result

## Images
### finplot
![Chart](https://github.com/StephanAkkerman/Live_Binance_Charts/blob/main/img/charts.png)

### mplfinance
![image](https://github.com/StephanAkkerman/live-binance-charts/assets/45365128/242ea434-809c-4b80-bec3-0059a8d1a3ae)

