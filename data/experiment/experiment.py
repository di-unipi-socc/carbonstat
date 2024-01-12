import os 
from requests import get
from time import sleep

# ------------------------
#   CONFIG
# ------------------------
# Config data
iterations = 2
csv_input_file = "csv/short_example.csv"
csv_output_file = "results_with_timestamps.csv"
csv_results_file = "results.csv"

power_consumption = 0.05 # worst-case power consumption of my laptop(kW) 


# Considered policies 
# (by assuming max_carbon=500 and max_reqs=1000)
policies = [
    # always running full power
    { "name": "a_full", "high": "10000,10000", "medium": "10000,10000"},
    # naive partitioning (three equal-sized chunks per dimension)
    { "name": "naive", "high": "170,333", "medium": "335,666"}, 
    # computed with policymaker
    # { "name": "found", "high": ",", "medium": ","},
    # always running low power
    { "name": "a_low", "high": "0,0", "medium": "0,0"}
]

# Logging (on file)
log = open("exp.log",mode="w",buffering=1)

# ------------------------
#   RUN
# ------------------------
log.write("* running experiments\n")
# open input csv file
csv_input = open(csv_input_file,mode="r")
# open output csv file (policy,timestamp,carbon,min_precision,average_precision)
csv_output = open(csv_output_file,mode="w",buffering=1)
csv_output.write("policy,timestamp,requests,carbon_emissions,min_precision,avg_precision\n")
# run queries for each timestamp
for line in list(csv_input)[1:]:
    # get timestamp, carbon, and requests
    # (by assuming CSV data like: "time,actual,forecast,reqs")
    data = line.replace("\n","").split(",")
    timestamp = data[0]
    carbon = int(data[1])
    requests = int(data[3])

    # run only if there are requests to simulate
    if requests > 0:
        # repeat run for all policies to be considered
        for policy in policies:
            # config experiment's deployment (from template)
            template_file = open("experiment-template.yml") 
            template = template_file.read()
            template_file.close()
            template = template.replace("$CARB",str(carbon))
            template = template.replace("$REQS",str(requests))
            template = template.replace("$HP_LIMITS",policy["high"])
            template = template.replace("$MP_LIMITS",policy["medium"])
            with (open("experiment-deploy.yml","w")) as experiment_deploy: 
                experiment_deploy.write(template)

            # repeat run for the given number of iterations
            total_carbon = 0
            min_precision = 100
            avg_precision = 0
            for i in range(iterations):
                log.write("policy: " + policy["name"] + "\ttimestamp: " + str(timestamp) + "\titeration: " + str(i+1) + "\n")

                # force re-build of image, to re-create dataset
                os.system("docker compose -f experiment-template.yml build --no-cache >> log.txt 2>> log.txt")

                # deploy configured experiment (and wait for deployment to complete)
                os.system("docker compose -f experiment-deploy.yml up -d >> log.txt 2>> log.txt")
                
                # force high power call to get correct result
                correct_avg = None
                while correct_avg is None:
                    sleep(1)
                    try: 
                        response = get("http://127.0.0.1:50000/avg?force=true").json()
                        correct_avg = float(response["value"])
                    except:
                        continue
            
                # send queries and process results
                ith_avg_precision = 0
                for j in range(requests):
                    # send query
                    response = get("http://127.0.0.1:50000/avg").json()
                    # measure carbon emission (considering carbon intensity, elapsed time, and power consumption)
                    carbon_intensity = float(response["carbon"])*1000 # mg of co2-eq/(kW*h)
                    elapsed_time = float(response["elapsed"])/(3600*1000) # elapsed hours for computation (h)
                    total_carbon += carbon_intensity * power_consumption * elapsed_time
                    # compute precision
                    deviation = abs(float(response["value"]) - correct_avg)
                    precision = 100 - round(deviation/correct_avg*100,2)
                    if precision < min_precision:
                        min_precision = precision
                    ith_avg_precision += precision
                ith_avg_precision = ith_avg_precision/requests # requests are assumed to be > 0
                avg_precision += ith_avg_precision

                # undeploy experiment
                os.system("docker compose -f experiment-deploy.yml down 2>> log.txt")

            # write results on the output csv file
            avg_precision = avg_precision/iterations
            csv_output.write(policy["name"] + "," + timestamp + "," + str(requests) + "," + str(total_carbon) + "," + str(round(min_precision,2)) + "," + str(round(avg_precision,2)) + "\n") 
# close input & output csv files
csv_input.close()
csv_output.close()

# ------------------------
#   POST-PROCESS
# ------------------------
log.write("* post-processing results\n")
# create object to store stats on each policy
stats = {}
for policy in policies: 
    stats[policy["name"]] = {}
    stats[policy["name"]]["carbon"] = 0
    stats[policy["name"]]["min_precision"] = 100
    stats[policy["name"]]["precisions"] = []

# extract data from csv output file
csv_output = open(csv_output_file,"r")
for line in list(csv_output)[1:]:
    # extract line data
    data = line.split(",")
    policy = data[0]
    requests = int(data[2])
    carbon = float(data[3])
    min_precision = float(data[4])
    avg_precision = float(data[5])
    # update policy's overall carbon emissions
    stats[policy]["carbon"] += carbon
    #  update policy's overall min precision
    if min_precision < stats[policy]["min_precision"]:
        stats[policy]["min_precision"] = min_precision
    # add [requests,avg_precision] to precisions (to later compute the policy's overall avg)
    stats[policy]["precisions"].append({"requests": requests, "avg_precision": avg_precision})
csv_output.close()

# compute each policy's overall avg precision
for policy in policies:
    tot_requests = 0
    avg_precision = 0
    for rp in stats[policy["name"]]["precisions"]:
        tot_requests += rp["requests"]
        avg_precision += rp["avg_precision"]*rp["requests"]
    stats[policy["name"]]["avg_precision"] = round(avg_precision/tot_requests,2)
    stats[policy["name"]].pop("precisions",None)

# write policy stats on csv
csv_results = open(csv_results_file,"w")
csv_results.write("policy,carbon_emissions,min_precision,avg_precision\n")
for policy in policies:
    csv_results.write(policy["name"] + ",")
    csv_results.write(str(stats[policy["name"]]["carbon"]) + ",")
    csv_results.write(str(stats[policy["name"]]["min_precision"]) + ",")
    csv_results.write(str(stats[policy["name"]]["avg_precision"]) + "\n")
csv_results.close()

# ------------------------
#   CLEAN
# ------------------------
log.close()
os.system("rm log.txt")