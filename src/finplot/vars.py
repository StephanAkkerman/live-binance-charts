# fplt.plots created are stored here
plots = {}

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
# symbol_data_dict = dict.fromkeys(symbol_list, pd.DataFrame())

# Save ax and ax_rsi here
axs_dict = {}

countdown = ""

assets = []
timeframes = []
row_count = 0
col_count = 0

usdt_mode = False

symbol_data_dict = {}

selected_coins = []

global_layout = None
window = None
