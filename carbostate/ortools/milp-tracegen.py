import requests
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import csv
import numpy as np
from sklearn_extra.cluster import KMedoids
import matplotlib.pyplot as plt
import random as rnd

# Specify the interval of days, the initial date and the number of clusters
rnd.seed(42) # for reproducibility
###################################################

# Downloads emissions data for one given date (day)
def download_emissions(date='2023-01-28T00:30Z'):
    fr = parser.parse(date)
    delta = timedelta(days = 1, hours= 0, minutes= 0)
    to = fr + delta

    headers = {
    'Accept': 'application/json'
    }

    url = 'https://api.carbonintensity.org.uk/intensity/' + fr.isoformat() + '/' + to.isoformat()
    
    r = requests.get(url, params={}, headers = headers)
    
    res = dict(r.json())['data']

    return res

# Generates a list of requests at each slot for a given day
def all_slots_from_peaks(peaks = [(4, 100), (8,500), (12, 1000), (16, 500), (20, 1000), (24,300)]):
    slots = []
    for k in range(len(peaks)):
        (h1, r1) = peaks[k]
        (h2, r2) = peaks[(k+1)%len(peaks)]

        diff = r2 - r1
        steps = 2 * (h2 - h1) % 24
        inc = diff // steps
    
        for i in range(steps):
            step = r1 + inc * i 
            slots.append(round(step))

    return slots

# Generates a list of requests for a given day, by varying them by +/- 10% of the baseline
def generate_event_trace(peaks = [(4, 100), (8,500), (12, 1000), (16, 500), (20, 1000), (24,300)]):
    events_at_slot_i = []

    baseline = all_slots_from_peaks()

    for reqs in baseline:
        events_at_slot_i += [int(reqs + rnd.uniform(-0.1,0.1) * reqs)]
            
    return events_at_slot_i

# Generates a trace for carbon emissions and requests for a given day
def generate_trace(init_date='2023-01-28T00:30Z'):
    emissions = download_emissions(init_date)

    reqs = generate_event_trace()

    return emissions, reqs

# Writes the time_slots.csv file with the (forecast and actual) emissions and requests for a given day
def print_files(init_date='2023-01-28T00:30Z'):
    emissions, reqs = generate_trace(init_date)
    half_hours = 48

    with open('time_slots1.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['time', 'strategy', 'actual_carbon', 'forecast_carbon', 'actual_reqs', 'forecast_reqs'])
        for i in range(0, half_hours):
            writer.writerow([emissions[i]['from'], emissions[i]['intensity']['actual'], emissions[i]['intensity']['forecast'], int(reqs[i]+reqs[i]*rnd.uniform(-0.05,0.05)), reqs[i]])


print_files()
