from argparse import ArgumentParser

# ------------------------
#    UTILITY 
# ------------------------
# Function to parse a line of the input csv file
def parse_input_line(line):
    line_data = line.replace("\n","").split(",")
    data = {}
    data["strategy"] = line_data[1]
    data["result"] = float(line_data[2])
    data["elapsed_time"] = float(line_data[3])
    data["error"] = float(line_data[4])
    return data

# Function to write a line of the output csv file
def write_output_line(output_file,results):
    if results is None:
        output_file.write("strategy,elapsed_time,error\n")
    else:
        output_file.write(str(results["strategy"]) + ",")
        output_file.write(str(round(results["elapsed_time"],4)) + ",")
        output_file.write(str(round(results["error"],4)) + "\n")

# ------------------------
#   RUN
# ------------------------
# Parse command-line arguments
parser = ArgumentParser("Run an iteration of the experiment")
parser.add_argument('input_file', type=str, help='Output CSV file')
parser.add_argument('output_file', type=str, help='Output CSV file')
args = parser.parse_args()

# Config data
strategies = ["HighPower","MediumPower","LowPower"]

# Collectors of aggregated results
results = {}
for s in strategies:
    results[s] = {}
    results[s]["strategy"] = s
    results[s]["elapsed_time"] = 0
    results[s]["error"] = 0
    results[s]["count"] = 0

# Read raw results
raw_results = open(args.input_file,"r")
for r_line in list(raw_results)[1:]:
    data = parse_input_line(r_line)
    s = data["strategy"]
    results[s]["elapsed_time"] += data["elapsed_time"]
    results[s]["error"] += data["error"]
    results[s]["count"] += 1
raw_results.close()

# Compute aggregated results
for s in strategies:
    results[s]["elapsed_time"] = results[s]["elapsed_time"]/results[s]["count"] 
    results[s]["error"] = results[s]["error"]/results[s]["count"] 

# Write results on file
res = open(args.output_file,"w")
write_output_line(res,None)
for s in strategies:
    write_output_line(res,results[s])
res.close()