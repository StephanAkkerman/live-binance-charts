from datetime import datetime

import pandas as pd

from binance.client import Client
from binance import ThreadedWebsocketManager

import vars

client = Client()
twm = ThreadedWebsocketManager()

# Get list of currently supported symbols
supported_symbols = [d["symbol"] for d in client.get_exchange_info().get("symbols")]


def start_kline_socket(symbol, interval):
    # Make a new websocket for this asset
    twm.start_kline_socket(symbol=symbol, callback=ws_response, interval=interval)


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

    # try:
    sym = info["s"]
    tf = info["k"]["i"]

    # Skip response if symbol is not in dict
    if sym not in vars.symbol_data_dict:
        return

    if tf != vars.preferred[sym]:
        return

    df = vars.symbol_data_dict[sym]

    close = float(info["k"]["c"])
    high = float(info["k"]["h"])
    low = float(info["k"]["l"])
    volume = float(info["k"]["v"])

    # t is the timestamp in ms
    t = int(info["k"]["t"])

    # Use int(info['k']['T']) - current time to calculate time untill next candle
    d1 = int(info["k"]["T"])
    converted_d1 = datetime.fromtimestamp(round(d1 / 1000))
    current_time = datetime.now()
    td = converted_d1 - current_time
    vars.countdown = str(td).split(".")[0]

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

        # Add to dataframe
        df = pd.concat([df, candle])

    # Symbol_dict consists of all ohlcv data
    vars.symbol_data_dict[sym] = df

    # Catch any exception
    # except Exception as e:
    #    print("Error handling websocket response")
    #    print(e)
