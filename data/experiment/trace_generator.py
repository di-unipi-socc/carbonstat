from argparse import ArgumentParser
import requests
from datetime import timedelta
from dateutil import parser as date_parser
import csv
import random as rnd
from os import system,listdir

# Function to initialize the environment for trace/assignment generation
def init(target_folder):
    # Create target folder (overwrite, if existing)
    system("rm -R " + target_folder)
    system("mkdir " + target_folder)
    # Copy files needed by carbonstat
    system("cp ../../carbonstat/carbonstat.py .")
    system("cp ../../carbonstat/test/strategies.csv .")

# Downloads emissions data for one given date (day)
def download_emissions(date='2023-01-28T00:30Z'):
    # Identify starting and end time slot
    fr = date_parser.parse(date)
    delta = timedelta(days = 1, hours= 0, minutes= 0)
    to = fr + delta
    # Send request to Carbon Intensity API
    headers = {'Accept': 'application/json'}
    url = 'https://api.carbonintensity.org.uk/intensity/' + fr.isoformat() + '/' + to.isoformat()  
    r = requests.get(url, params={}, headers = headers)  
    # Return values
    res = dict(r.json())['data']
    return res

# Function to generates a list of requests at each 30-min slot for a given day
def generate_reqs_trace(peaks = [(4, 100), (8,500), (12, 1000), (16, 500), (20, 1000), (24,300)]):
    slots = []
    for k in range(len(peaks)):
        (h1, r1) = peaks[k]
        (h2, r2) = peaks[(k+1)%len(peaks)]

        diff = r2 - r1
        steps = 2 * (h2 - h1) % 24
        inc = diff // steps
    
        for i in range(steps):
            step = r1 + inc * i 
            res = step * (1 + rnd.uniform(-0.1,0.1))
            slots.append(round(res))

    return slots

# Function to generate carbon/req traces and write them on csv files
def generate_csv_values(start_date,days,step,profile,target_folder):
    # rnd.seed(42) # uncomment, for reproducibility
    # Create folder for "values"
    values_folder = target_folder + "/values"
    system("mkdir " + values_folder)

    # Repeat generation from "start_date" for given days
    for d in range(days):
        # Download emissions
        date = date_parser.parse(start_date) + timedelta(days=d*step,hours=0,minutes=0)
        emissions = download_emissions(date.isoformat())
        # Generate requests
        reqs = None
        if profile == "stable":
            reqs = generate_reqs_trace(peaks = [(4, 300), (8, 300), (12, 300), (16, 300), (20, 300), (24, 300)])
        else: 
            reqs = generate_reqs_trace()
        # Write emissions and requests on CSV file
        file = values_folder + "/m"
        file += "0" + str(d+1) if d < 9 else str(d+1)
        file += ".csv"
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['time', 'actual_carbon', 'forecast_carbon', 'actual_reqs', 'forecast_reqs'])
            for i in range(0, 48):
                writer.writerow([emissions[i]['from'], emissions[i]['intensity']['actual'], emissions[i]['intensity']['forecast'], int(reqs[i]+reqs[i]*rnd.uniform(-0.05,0.05)), reqs[i]])    

# Runs carbonstat on the given inputs
def run_carbonstat(input_time_slots,error_threshold,output_assignment):
    cmd = "python3 carbonstat.py "
    cmd += input_time_slots + " "
    cmd += "strategies.csv "
    cmd += str(error_threshold) + " "
    cmd += output_assignment
    # run carbonstat
    system(cmd)

# Function to generate carbonstat's assignments
def generate_assignment(error_threshold,target_folder):
    # Create assignment folder
    assignment_folder = target_folder + "/error_"
    assignment_folder += "0" + str(error_threshold) if error_threshold < 10 else str(error_threshold)
    system("mkdir " + assignment_folder)
    # Run carbonstat on all available days
    values_folder = target_folder + "/values" 
    days = listdir(values_folder)
    for day in days:
        input_time_slots = values_folder + "/" + day
        output_assignment = assignment_folder + "/assignment_" + day
        run_carbonstat(input_time_slots,error_threshold,output_assignment)    

# ------------------------
#    RUN
# ------------------------ 
# Parse command-line arguments
parser = ArgumentParser("Run an iteration of the experiment")
parser.add_argument('profile', type=str, help="Profile of requests (supported: stable,camel)")
parser.add_argument('target_folder', type=str, help='Folder where to put generated traces/assignments')
args = parser.parse_args()

# Init trace generation
init(args.target_folder)

# Create traces
if args.profile not in ['stable','camel']:
    print("ERR: Unsupport profile for requests generation")
    exit(-1)

generate_csv_values("2023-01-28T00:30Z",12,28,args.profile,args.target_folder)

for err in [1,2,4,8]:
    generate_assignment(err,args.target_folder)