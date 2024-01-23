import os 
from requests import get
from time import sleep

# ------------------------
#   CONFIG
# ------------------------
# Config data
power_consumption = 0.05 # worst-case power consumption of my laptop(kW) 
max_carbon = 450
max_reqs = 1000
iterations = 2

csv_input_file = "csv/short_example.csv"
csv_output_file = "results_with_timestamps.csv"
csv_results_file = "results.csv"

# Considered policies 
# (by assuming max_carbon and max_reqs as above)
policies = [
    # always running full power
    { "name": "a_full", "high": "10000,10000", "medium": "10000,10000"},
    # naive partitioning (three equal-sized chunks per dimension)
    # { "name": "naive", "high": str(round(5+max_carbon/3)) + "," + str(round(max_reqs/3)), "medium": str(round(5+max_carbon*2/3)) + "," + str(round(max_reqs*2/3))}, 
    # computed with policymaker
    # { "name": "found", "high": ",", "medium": ","},
    # always running medium power
    { "name": "a_med", "high": "0,0", "medium": "10000,10000"},
    # always running low power
    { "name": "a_low", "high": "0,0", "medium": "0,0"}
]

# Logging (on file)
log = open("exp.log",mode="w",buffering=1)
os.system("rm log.txt")

# ------------------------
#   RUN
# ------------------------
log.write("* running experiments\n")
# open input csv file
csv_input = open(csv_input_file,mode="r")
# open output csv file (policy,timestamp,carbon,max_error,avg_error,avg_time)
csv_output = open(csv_output_file,mode="w",buffering=1)
csv_output.write("policy,timestamp,requests,carbon_emissions,max_error,avg_error,avg_time\n")
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
            max_error = 0
            avg_error = 0
            avg_time = 0
            for i in range(iterations):
                log.write("policy: " + policy["name"] + "\ttimestamp: " + str(timestamp) + "\titeration: " + str(i+1) + "\n")

                # force re-build of image to re-create dataset
                os.system("docker rmi carbon-aware-service >> log.txt 2>> log.txt")
                os.system("docker compose -f experiment-template.yml build >> log.txt 2>> log.txt")

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
                ith_avg_error = 0
                ith_avg_time = 0
                for j in range(requests):
                    # send query
                    response = get("http://127.0.0.1:50000/avg").json()
                    # measure elapsed time
                    elapsed_time = float(response["elapsed"])
                    ith_avg_time += elapsed_time
                    elapsed_hours = elapsed_time/(3600*1000) # elapsed hours for computation (h)
                    # measure carbon emission (considering carbon intensity, elapsed time, and power consumption)
                    carbon_intensity = float(response["carbon"])*1000 # mg of co2-eq/(kW*h)
                    total_carbon += round(carbon_intensity * power_consumption * elapsed_hours,2)
                    # compute precision
                    deviation = abs(float(response["value"]) - correct_avg)
                    error = round(deviation/correct_avg*100,2)
                    if error > max_error:
                        max_error = error
                    ith_avg_error += error
                ith_avg_error = ith_avg_error/requests # requests are assumed to be > 0
                avg_error += ith_avg_error
                ith_avg_time = ith_avg_time/requests # requests are assumed to be > 0
                avg_time += ith_avg_time

                # undeploy experiment
                os.system("docker compose -f experiment-deploy.yml down 2>> log.txt")

            # write results on the output csv file
            avg_error = avg_error/iterations
            avg_time = avg_time/iterations
            csv_output.write(policy["name"] + "," + timestamp + "," + str(requests) + "," + str(round(total_carbon,2)) + "," + str(round(max_error,2)) + "," + str(round(avg_error,2)) + "," + str(round(avg_time,2)) + "\n") 
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
    stats[policy["name"]]["max_error"] = 100
    stats[policy["name"]]["stats"] = []

# extract data from csv output file
csv_output = open(csv_output_file,"r")
for line in list(csv_output)[1:]:
    # extract line data
    data = line.split(",")
    policy = data[0]
    requests = int(data[2])
    carbon = float(data[3])
    max_error = float(data[4])
    avg_error = float(data[5])
    avg_time = float(data[6])
    # update policy's overall carbon emissions
    stats[policy]["carbon"] += carbon
    #  update policy's overall min precision
    if max_error < stats[policy]["max_error"]:
        stats[policy]["max_error"] = max_error
    # add [requests,avg_error] to precisions (to later compute the policy's overall avg)
    stats[policy]["stats"].append({"requests": requests, "avg_error": avg_error, "avg_time": avg_time})
csv_output.close()

# compute each policy's overall avg precision
for policy in policies:
    tot_requests = 0
    avg_error = 0
    avg_time = 0
    for rp in stats[policy["name"]]["stats"]:
        tot_requests += rp["requests"]
        avg_error += rp["avg_error"]*rp["requests"]
        avg_time += rp["avg_time"]*rp["requests"]
    stats[policy["name"]]["avg_error"] = round(avg_error/tot_requests,2)
    stats[policy["name"]]["avg_time"] = round(avg_time/tot_requests,2)
    stats[policy["name"]].pop("stats",None)

# write policy stats on csv
csv_results = open(csv_results_file,"w")
csv_results.write("policy,carbon_emissions,max_error,avg_error,avg_time\n")
for policy in policies:
    csv_results.write(policy["name"] + ",")
    csv_results.write(str(stats[policy["name"]]["carbon"]) + ",")
    csv_results.write(str(stats[policy["name"]]["max_error"]) + ",")
    csv_results.write(str(stats[policy["name"]]["avg_error"]) + ",")
    csv_results.write(str(stats[policy["name"]]["avg_time"]) + "\n")
csv_results.close()

# ------------------------
#   CLEAN
# ------------------------
log.close()