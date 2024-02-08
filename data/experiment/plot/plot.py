from os import listdir

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
    hist_data["x"] = [] # x-axis: list of strategy names
    hist_data["y"] = [] # y-axis: list of [saved_co2,error] for each strategy
    for s in data["strategies"]:
        if not s == "always_high":
            # get x data (strategy name)
            hist_data["x"].append(s)
            # get y data (saved_co2,error)
            s_data = []
            s_data.append(saved(s,data))
            s_data.append(data["strategies"][s]["avg_error"])
            hist_data["y"].append(s_data)
    return hist_data

# ----------------------
#  RUN
# ----------------------

# Get names of result files to be plotted
result_files = listdir(".")
result_files = filter(lambda x : x.startswith("results"),result_files)

# Plot a different histogram chart for each result file
for f_name in result_files:
    res = parse_results(f_name)
    hist_data = prepare_hist(res)
    print(hist_data)