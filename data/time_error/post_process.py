# ------------------------
#   POST-PROCESS 
# ------------------------

# Data structure
strategies = ["HighPower","MediumPower","LowPower"]
avg_time = {}
avg_error = {}
count = {}
for s in strategies:
    avg_time[s] = 0
    avg_error[s] = 0
    count[s] = 0

# Read raw results
raw_results = open("results_raw.csv","r")
for result in list(raw_results)[1:]:
    data = result.replace("\n","").split(",")
    strategy = data[1]
    avg_time[strategy] += float(data[3])
    avg_error[strategy] += float(data[4])
    count[strategy] += 1
raw_results.close()

# Compute aggregated results
for s in strategies:
    avg_time[s] = round(avg_time[s]/count[s],2)
    avg_error[s] = round(avg_error[s]/count[s],2)

# Write results on file
results = open("results.csv","w")
results.write("strategy,duration,error,count\n")
for s in strategies:
    results.write(s + ",")
    results.write(str(avg_time[s]) + ",")
    results.write(str(avg_error[s]) + ",")
    results.write(str(count[s]) + "\n")
results.close()