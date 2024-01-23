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
days = 1
init_date = '2023-01-01T00:00Z'
asp_time_limit = 2
###################################################

half_hours = 48 * days
delta = timedelta(days = days, hours= 0, minutes= 0)

fr = parser.parse(init_date)
to = fr + delta

print('### Downloading carbon emissions for the period from ' + fr.isoformat() + ' to ' + to.isoformat())

headers = {
  'Accept': 'application/json'
}
url = 'https://api.carbonintensity.org.uk/intensity/' + fr.isoformat() + '/' + to.isoformat()
 
r = requests.get(url, params={}, headers = headers)
 
res = dict(r.json())['data']

print('### Done!')

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

def generate_event_trace(days, peaks = [(4, 100), (8,500), (12, 1000), (16, 500), (20, 1000), (24,300)]):
    events_at_slot_i = []

    baseline = all_slots_from_peaks()

    for d in range(days):
        for reqs in baseline:
            events_at_slot_i += [int(reqs + rnd.uniform(-0.1,0.1) * reqs)]
            
    return events_at_slot_i

print('### Generating events trace')

events_at_slot_i = generate_event_trace(days)

print('### Done!')


carbon = []

print('### Writing data to files')

for i in range(0, half_hours):
    carbon.append(res[i]['intensity']['forecast'])

data = list(zip(carbon, events_at_slot_i))

with open('input.lp', 'w') as inputfile:
    inputfile.write('maxError(6).\n')
    
    inputfile.write('\n')
    inputfile.write('strategy(0, 1, 15).\nstrategy(1, 2, 5).\nstrategy(2, 3, 0).\n')
    inputfile.write('\n')

    for i in range(0, half_hours):
        inputfile.write('timeslot(' + str(i+1) + ', ' + str(round(res[i]['intensity']['forecast']/3.6)) + ', ' + str(round(events_at_slot_i[i]/100)) + ').\n')
                                                      

print('### Done!')


from clyngor import ASP, solve

def solving(main, input):
    programs = [main, input]
    clasp_options = '--opt-mode=optN', '--parallel-mode=16', '--project', '--time-limit='+str(asp_time_limit)
    answers = solve(programs, options=clasp_options, stats=True)
    print("solver run as: `{}`".format(answers.command))
    for answerset in answers.with_optimality: #.as_pyasp:
        yield answerset

answers = solving('policy_maker.pl', 'input.lp')

loaded = []
foundOpt = False

for (a, (c1,c2), optimal) in answers:
    loaded.append((c1,c2,a,optimal))

    if optimal:
        print("Optimal solution found")
        #print(c1,c2,a,optimal)
        foundOpt = True
        break

if not foundOpt:
    print("No optimal solution found")
    loaded = sorted(loaded)
    #print(loaded[0])


strategies = sorted([ts[1] for ts in loaded[0][2]])
strategies = [s for (_,s) in strategies]


print('### Writing data to files')
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['time', 'strategy', 'actual_carbon', 'forecast_carbon', 'actual_reqs', 'forecast_reqs'])
    for i in range(0, half_hours):
        writer.writerow([res[i]['from'], strategies[i], res[i]['intensity']['actual'], res[i]['intensity']['forecast'], int(events_at_slot_i[i]+events_at_slot_i[i]*rnd.uniform(-0.1,0.1)), events_at_slot_i[i]])