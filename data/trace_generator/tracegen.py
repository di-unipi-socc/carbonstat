import requests
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import csv
import numpy as np
from sklearn_extra.cluster import KMedoids
import matplotlib.pyplot as plt
import random as rnd
from os import system

# Downloads emissions data for one given date (day)
def download_emissions(date='2023-01-28T00:30Z'):
    fr = parser.parse(date)
    delta = timedelta(days = 1, hours= 0, minutes= 0)
    to = fr + delta

    headers = {'Accept': 'application/json'}

    url = 'https://api.carbonintensity.org.uk/intensity/' + fr.isoformat() + '/' + to.isoformat()
    
    r = requests.get(url, params={}, headers = headers)
    
    res = dict(r.json())['data']

    return res

# Generates a list of requests at each slot for a given day
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

# Generates a trace for carbon emissions and requests for a given day
def generate_traces(date='2023-01-28T00:30Z'):
    emissions = download_emissions(date)
    reqs = generate_reqs_trace()
    return emissions, reqs

# Writes the time_slots.csv file with the (forecast and actual) emissions and requests for a given day
def traces_to_file(date='2023-01-28T00:30Z'):
    emissions, reqs = generate_traces(date)

    with open('time_slots.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['time', 'actual_carbon', 'forecast_carbon', 'actual_reqs', 'forecast_reqs'])
        for i in range(0, 48):
            writer.writerow([emissions[i]['from'], emissions[i]['intensity']['actual'], emissions[i]['intensity']['forecast'], int(reqs[i]+reqs[i]*rnd.uniform(-0.05,0.05)), reqs[i]])

def carbostat(input_time_slots,input_strategies,error_threshold,output_assignment):
    cmd = "python3 ../../carbostat/carbostat.py "
    cmd += input_time_slots + " "
    cmd += input_strategies + " "
    cmd += error_threshold + " "
    cmd += output_assignment
    # run carbostat
    system.cmd(cmd)
    
def run(seed=42, error_threshold=9, init_date='2023-01-28T00:30Z',days = 12, step = 28):
    rnd.seed(seed) # for reproducibility

    for d in range(days):
        traces_to_file(init_date)
        input_time_slots = "time_slots.csv"
        input_strategies = "strategies.csv"
        output_assignment = "./traces/"+str(error_threshold)+"/assignment_m"+str(d+1)+".csv"
        carbostat(input_time_slots,input_strategies,error_threshold,output_assignment)
        init_date = (parser.parse(init_date) + timedelta(days=step)).isoformat()

# ------------------------
#    RUN
# ------------------------ 
for err in [1,2,4,5,8,10,12,15]:
    run(error_threshold=err)