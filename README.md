# Live Binance Charts
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/github/license/StephanAkkerman/Live_Binance_Charts.svg?color=brightgreen)](https://opensource.org/licenses/MIT)

---
This is a simple Python script showing multiple live charts of assets available on Binance.

## Implementations
### finplot
The most advance implementation of this project uses finplot and PyQt6 for plotting. This is a more advanced library for plotting in Python.

### mplfinance
The other implementation uses mplfinance, which is based on matplotlib, a very popular plotting library. In `src/mplfinance/keys.py` you can specify your Binance API keys so that the chart automatically plots your assets. You can also leave this empty and specify the coins manually.

## Features
- Dark mode Tradingview style display
- Remove or add charts to view
- Real time updates, using the Binance websocket

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

