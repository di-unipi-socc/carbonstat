from os import listdir
from matplotlib import pyplot as plt
import numpy as np

# Function to parse the results contained in a given file
def parse_results(file_name):
    r = {}
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
            hist_data["labels"].append(s.replace("_","\n"))
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
    
    # Plot setup
    bar_width = 0.35
    plt.rcParams['font.family'] = 'Helvetica'
    plt.rcParams['font.size'] = '25'
    plt.figure(figsize=(15, 6))

    # Setting x axis
    x = np.arange(len(hist_data["labels"]))
    plt.xticks(x, hist_data["labels"])  

    # Setting y axis
    max_y = 70
    plt.yticks(np.arange(0, max_y, 10))
    for y in np.arange(5, max_y, 5):
        plt.axhline(y, color='grey', linestyle='dotted')

    # Displaying bars
    plt.bar(x - bar_width/2, hist_data["saved_co2"], width=bar_width, label='Emission reduction')
    plt.bar(x + bar_width/2, hist_data["error"], width=bar_width, label='Average error')

    # Printout
    plt.legend()
    plt.tight_layout()
    plt.savefig(f_name.split(".")[0] + ".pdf")
