from os import path
import pickle

import vars


# Gets preferred settings at start up
def get_preferred():
    file = "settings.pkl"
    nr_charts = 4  # Remove this if more charts look nicer

    if path.exists(file):
        print("Found settings")

        # Get preffered pickle
        with open(file, "rb") as handle:
            preferred = pickle.load(handle)

        if preferred == {}:
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

    # Set global variables
    # vars.preferred = preferred
    # vars.symbol_list = symbol_list
    # vars.nr_charts = nr_charts
    preferred = {k: preferred[k] for k in list(preferred)[:nr_charts]}

    return preferred


# Do this if the save button is pressed
def save_settings():
    file = "settings.pkl"

    # Write currently prefferd as pickle
    with open(file, "wb") as handle:
        pickle.dump(vars.preferred, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Saved settings")
