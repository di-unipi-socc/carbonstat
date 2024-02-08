from os import listdir
from matplotlib import pyplot as plt
import numpy as np

# Function to parse the results contained in a given file
def parse_results(file_name):
    r = {}
    r["error_threshold"] = int(f_name.split(".")[0].split("_")[-1])
    r["strategies"] = {}
    file = open(file_name,"r")
    for result in list(file)[1:]:
        raw_data = result.replace("\n","").split(",")
        strategy = raw_data[0]
        r["strategies"][strategy] = {}
        r["strategies"][strategy]["carbon"] = float(raw_data[1])
        r["strategies"][strategy]["avg_error"] = float(raw_data[2])
        # r["strategies"][strategy]["max_error"] = raw_data[3]  
    file.close()
    r["max_carbon"] = r["strategies"]["always_high"]["carbon"]
    return r

# Utility function to compute percentage of saved carbon
def saved(strategy,data):
    strategy_co2 = data["strategies"][strategy]["carbon"]
    max_co2 = data["max_carbon"]
    saved_co2 = max_co2 - strategy_co2
    return round(saved_co2*100/max_co2,2)

# Function to prepare histogram data
def prepare_hist(data):
    hist_data = {}
    hist_data["labels"] = [] # x-axis: list of strategy names
    hist_data["saved_co2"] = [] # y-axis: list of saved_co2 for each strategy
    hist_data["error"] = [] # y-axis: list of error for each strategy
    for s in data["strategies"]:
        if not s == "always_high":
            # get x data (strategy name)
            hist_data["labels"].append(s)
            # get y data (saved_co2,error)
            hist_data["saved_co2"].append(saved(s,data))
            hist_data["error"].append(data["strategies"][s]["avg_error"])
    return hist_data

# ----------------------
#  RUN
# ----------------------

# Get names of result files to be plotted
result_files = listdir(".")
result_files = filter(lambda x : x.startswith("results") and x.endswith("csv"),result_files)

# Plot a different histogram chart for each result file
for f_name in result_files:
    res = parse_results(f_name)
    hist_data = prepare_hist(res)
    
    # Plot setting (with two adjacent subplots)
    bar_width = 0.35
    plt.rcParams['font.family'] = 'Helvetica'
    x = np.arange(len(hist_data["labels"]))
    
    plt.figure(figsize=(12, 5))
    plt.bar(x - bar_width/2, hist_data["saved_co2"], width=bar_width, label='Emission reduction')
    plt.bar(x + bar_width/2, hist_data["error"], width=bar_width, label='Average error')

    threshold = res["error_threshold"]
    # plt.axhline(y=threshold, color='black', linestyle='dotted', label='Tolerated error')

    plt.xticks(x, hist_data["labels"])  # Posiziona le etichette sull'asse x
    plt.legend()

    # Regola lo spazio tra i grafici per evitare sovrapposizioni
    plt.tight_layout()
    plt.savefig(f_name.split(".")[0] + ".pdf")
    # plt.show()
