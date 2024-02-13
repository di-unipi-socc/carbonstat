from argparse import ArgumentParser

# Collector for the experiment's aggregated results
res = {}
# List of considered policies
policies = [] # ["always_low","always_medium","always_high","naive","carbostat_e=1","carbostat_e=2","carbostat_e=4","carbostat_e=8"]

# ------------------------
#    UTILITY 
# ------------------------

# Function to add a record to "res" concerning a given policy
def add_policy(p):
    policies.append(p)
    res[p] = {}
    res[p]["policy"] = p
    res[p]["total_reqs"] = 0
    res[p]["carbon"] = 0
    res[p]["avg_error"] = 0
    res[p]["max_error"] = 0

# Function to parse a line of the input csv file
def parse_input_line(line):
    line_data = line.replace("\n","").split(",")
    data = {}
    data["timestamp"] = line_data[0]
    policy = line_data[1]
    if not (policy in res):
        add_policy(policy)
    data["policy"] = policy
    data["total_reqs"] = int(line_data[2])
    data["carbon"] = float(line_data[3])
    data["avg_error"] = float(line_data[4])
    data["max_error"] = float(line_data[5])
    return data

# Function to write a line of the output csv file
def write_output_line(output_file,results):
    if results is None:
        output_file.write("policy,carbon,avg_error,max_error\n")
    else:
        output_file.write(str(results["policy"]) + ",")
        output_file.write(str(round(results["carbon"],2)) + ",")
        output_file.write(str(round(results["avg_error"],2)) + ",")
        output_file.write(str(round(results["max_error"],2)) + "\n")

# ------------------------
#    RUN
# ------------------------ 
# Parse command-line arguments
parser = ArgumentParser("Post-processing of the experiment's results")
parser.add_argument('input_file', type=str, help='File with raw results')
parser.add_argument('output_file', type=str, help='File with aggregated results')
args = parser.parse_args()

# Aggregation of the experiment's results
input_file = open(args.input_file,"r")
for line in list(input_file)[1:]:
    data = parse_input_line(line)
    policy_res = res[data["policy"]]
    policy_res["total_reqs"] += data["total_reqs"]
    policy_res["carbon"] += data["carbon"]
    policy_res["avg_error"] += data["avg_error"]*data["total_reqs"]
    if data["max_error"] > policy_res["max_error"]: 
        policy_res["max_error"] = data["max_error"]
input_file.close()

print(policies)

# Complete aggregation
for p in policies:
    policy_res = res[p]
    if policy_res["total_reqs"] > 0:
        policy_res["avg_error"] = policy_res["avg_error"]/policy_res["total_reqs"]

# Write results on output file
output_file = open(args.output_file,"w")
write_output_line(output_file,None)
for p in policies:
    write_output_line(output_file,res[p])
output_file.close()