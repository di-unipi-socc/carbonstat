from os import listdir

def parse_results(file_name):
    r = {}
    r["error_threshold"] = int(f_name.split(".")[0].split("_")[-1])
    r["strategies"] = {}
    file = open(file_name,"r")
    for result in list(file)[1:]:
        raw_data = result.replace("\n","").split(",")
        strategy = raw_data[0]
        r["strategies"][strategy] = {}
        r["strategies"][strategy]["carbon"] = raw_data[1]
        r["strategies"][strategy]["avg_error"] = raw_data[2]
        # r["strategies"][strategy]["max_error"] = raw_data[3]  
    file.close()
    r["max_carbon"] = r["strategies"]["always_high"]["carbon"]
    return r

# Get names of result files to be plotted
result_files = listdir(".")
result_files = filter(lambda x : x.startswith("results"),result_files)

# Plot a different histogram chart for each result file
for f_name in result_files:
    res = parse_results(f_name)
    print(res)