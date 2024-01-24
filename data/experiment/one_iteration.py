from argparse import ArgumentParser
from os import system
from requests import get
from time import sleep
from uuid import uuid1
import logging

# ------------------------
#    UTILITY 
# ------------------------
# Function to parse a line of the input csv file
def parse_input_line(line):
    line_data = line.replace("\n","").split(",")
    data = {}
    data["timestamp"] = line_data[0]
    data["strategy"] = line_data[1]
    data["actual_carbon"] = int(line_data[2])
    data["forecast_carbon"] = int(line_data[3])
    data["actual_reqs"] = int(line_data[4])
    data["forecast_reqs"] = int(line_data[5])
    return data

# Function to write a line of the output csv file
def write_output_line(output_file,results):
    if results is None:
        output_file.write("timestamp,policy,total_reqs,carbon,avg_error,max_error\n")
    else:
        output_file.write(str(results["timestamp"]) + ",")
        output_file.write(str(results["policy"]) + ",")
        output_file.write(str(results["total_reqs"]) + ",")
        output_file.write(str(results["carbon"]) + ",")
        output_file.write(str(results["avg_error"]) + ",")
        output_file.write(str(results["max_error"]) + "\n")

# Function to compute the emissions in a given "elapsed_time" (in ms) with a given "carbon_intensity" (in g of co2-eq/(kW*h))
def emissions(elapsed_time,carbon_intensity):
    power_consumption = 0.05 # in KWh (representing a server consuming 50 Watt per hour)
    hours = elapsed_time/(3600*1000) # elapsed hours for computation
    mg_co2_kwh = carbon_intensity*1000 # mg of co2-eq/(kW*h)
    return mg_co2_kwh * power_consumption * hours

# ------------------------
#    SIMULATORS 
# ------------------------

# Function to simulate the execution of the "always_low" policy
def run_always_low(data):
    results = run_strategy("LowPower",data) 
    results["policy"] = "always_low"
    return results

# Function to simulate the execution of the "always_medium" policy
def run_always_medium(data):
    results = run_strategy("MediumPower",data) 
    results["policy"] = "always_medium"
    return results

# Function to simulate the execution of the "always_high" policy
def run_always_high(data):
    results = run_strategy("HighPower",data) 
    results["policy"] = "always_high"
    return results

# Function to simulate the execution of the "naive" policy
def run_naive(data):
    results = {}
    if data["forecast_carbon"] < 110 and data["forecast_reqs"] < 330:
        results = run_strategy("HighPower",data)
    elif data["forecast_carbon"] < 200 and data["forecast_reqs"] < 660: 
        results = run_strategy("MediumPower",data)
    else: 
        results = run_strategy("LowPower",data)
    results["policy"] = "naive"
    return results

# Function to simulate the execution of the "carbostate" policy
def run_carbostate(data):
    results = run_strategy(data["strategy"],data)
    results["policy"] = "carbostate"
    return results

# Function to execute a given strategy "s" on the input "data"
def run_strategy(s,data):
    # Collector of results
    results = {}
    results["timestamp"] = data["timestamp"]
    results["total_reqs"] = data["actual_reqs"]
    results["avg_error"] = 0
    results["max_error"] = 0
    results["avg_time"] = 0
    results["carbon"] = 0

    # Loop for sending (actual) requests
    for i in range(data["actual_reqs"]):
        # Send request
        response = get("http://127.0.0.1:50000/avg?force="+s).json()
        # Measure error
        deviation = abs(float(response["value"]) - data["correct_avg"])
        error = round(deviation/data["correct_avg"]*100,2)
        results["avg_error"] += error
        results["max_error"] = error if error > results["max_error"] else results["max_error"]
        # Measure elapsed time
        elapsed_time = float(response["elapsed"])
        results["avg_time"] += elapsed_time
        # Estimate carbon emission
        results["carbon"] += emissions(elapsed_time,data["actual_carbon"])
    
    # Compute aggregated values and round them to max two decimals
    results["avg_error"] = round(results["avg_error"]/results["total_reqs"],2)
    results["avg_time"] = round(results["avg_time"]/results["total_reqs"],2)
    results["carbon"] = round(results["carbon"],2)

    # Return collected results
    return results

# ------------------------
#    RUN ITERATION
# ------------------------
# Function to run an iteration of the experiment
def run_iteration(input_file,output_file):
    # Open input and output files
    csv_input = open(input_file,"r")
    csv_output = open(output_file,"a",buffering=1)

    # Logging 
    id = str(uuid1())
    preamble = id + ": "
    logging.basicConfig(level=logging.INFO,format='%(message)s', filename='experiment.log', filemode='a')
    logging.info("Starting iteration " + id + " (input file=" + input_file +")")

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
    
    # Simulate requests for each timestamp (after the starting_timestamp)
    for line in list(csv_input)[1:]:
        data = parse_input_line(line)
        data["correct_avg"] = correct_avg

        # Skip line if there are no requests to simulate
        if data["actual_reqs"] == 0:
            continue
        logging.info(preamble + "Considering time slot " + data["timestamp"])

        # Run "always_low" policy
        results = run_always_low(data)
        write_output_line(csv_output,results)
        logging.info(preamble + "Simulation of 'always_low' completed")
        
        # Run "always_medium" policy
        results = run_always_medium(data)
        write_output_line(csv_output,results)
        logging.info(preamble + "Simulation of 'always_medium' completed")
        
        # Run "always_high" policy
        results = run_always_high(data)
        write_output_line(csv_output,results)
        logging.info(preamble + "Simulation of 'always_high' completed")
        
        # Run "naive" policy
        results = run_naive(data)
        write_output_line(csv_output,results)
        logging.info(preamble + "Simulation of 'naive' completed")
        
        # Run "carbostate" policy
        results = run_carbostate(data)
        write_output_line(csv_output,results)
        logging.info(preamble + "Simulation of 'carbostate' completed")

    # Undeploy application
    system("docker compose down >> /dev/null 2>> /dev/null")

    # Close input and output files
    csv_input.close()
    csv_output.close()
    logging.info("- - - - - - - -")

# ------------------------
#    RUN 
# ------------------------
# Parse command-line arguments
parser = ArgumentParser("Run an iteration of the experiment")
parser.add_argument('input_file', type=str, help='Input CSV file')
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
    run_iteration(args.input_file,args.output_file)
except Exception as e:
   logging.error("An error occurred: " + e)