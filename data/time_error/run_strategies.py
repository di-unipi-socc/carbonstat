from argparse import ArgumentParser
from os import system 
from requests import get
from time import sleep
from uuid import uuid1
import logging

# ------------------------
#    UTILITY 
# ------------------------
# Function to write a line of the output csv file
def write_output_line(output_file,results):
    if results is None:
        output_file.write("iteration,strategy,result,elapsed_time,error\n")
    else:
        output_file.write(str(results["iteration"]) + ",")
        output_file.write(str(results["strategy"]) + ",")
        output_file.write(str(results["result"]) + ",")
        output_file.write(str(round(results["elapsed_time"],4)) + ",")
        output_file.write(str(round(results["error"],4)) + "\n")
    
# Function to execute a given strategy "s" for a given number of "reqs" (in a given "iteration" and knowing the "correct_avg")
def run_strategy(s,reqs,iteration,correct_avg):
    # Collector of results
    results = {}
    results["iteration"] = iteration
    results["strategy"] = s
    results["result"] = 0
    results["elapsed_time"] = 0
    results["error"] = 0
    
    # Loop for sending (actual) requests
    for i in range(reqs):
        # Send request
        response = get("http://127.0.0.1:50000/avg?force="+s).json()
        # Store result
        result = float(response["value"])
        results["result"] += result
        # Measure error
        error = abs(result - correct_avg)/correct_avg*100
        results["error"] += error 
        # Measure elapsed time
        elapsed_time = float(response["elapsed"])
        results["elapsed_time"] += elapsed_time
    
    # Compute aggregated values
    results["result"] = results["result"]/reqs
    results["elapsed_time"] = results["elapsed_time"]/reqs
    results["error"] = results["error"]/reqs
    
    # Return collected results
    return results

# ------------------------
#   RUN
# ------------------------
# Config data
requests = 100
strategies = ["HighPower","MediumPower","LowPower"]

# ------------------------
#    RUN ITERATION
# ------------------------
# Function to run an iteration of the experiment
def run_iteration(output_file):
    # Create data collectors
    times = {}
    errors = {}
    for s in strategies:
        times[s] = 0
        errors[s] = 0

    # Logging 
    id = str(uuid1())
    preamble = id + ": "
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        filename='experiment.log', filemode='a')
    logging.info("Starting iteration " + id)

    # Force re-build of image (to re-create dataset) and deploy application
    system("docker rmi carbon-aware-service >> /dev/null 2>> /dev/null")
    system("docker compose build >> /dev/null 2>> /dev/null")
    system("docker compose up -d >> /dev/null 2>> /dev/null")
    logging.info(preamble + "Application re-created and deployed")
                    
    # Force "HighPower" request to get the correct_avg
    correct_avg = None
    while correct_avg is None:
        sleep(1)
        try: 
            response = get("http://127.0.0.1:50000/avg?force=HighPower").json()
            correct_avg = float(response["value"])
        except:
            continue
    logging.info(preamble + "Correct average acquired")
        
    # Run each available strategy
    raw_results = open(output_file,"a",buffering=1)
    for s in strategies:
        results = run_strategy(s,requests,id,correct_avg)         
        write_output_line(raw_results,results)
        logging.info(preamble + "Strategy " + s + " done")
    raw_results.close()

    # Undeploy application
    system("docker compose down >> /dev/null 2>> /dev/null")
    logging.info("- - - - - - - -")

# ------------------------
#    RUN 
# ------------------------
# Parse command-line arguments
parser = ArgumentParser("Run an iteration of the experiment")
parser.add_argument('output_file', type=str, help='Output CSV file')
parser.add_argument('--init', action='store_true', help='Force re-creation of output CSV file')
args = parser.parse_args()

# Re-create output file if required
if args.init:
    output_file = open(args.output_file,"w")
    write_output_line(output_file,None)
    output_file.close()

# Run iteration
try:
    run_iteration(args.output_file)
except Exception as e:
   logging.error("An error occurred: " + e)