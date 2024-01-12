import requests
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import csv
import numpy as np


# Specify the interval of days and the initial date
days = 2
init_date = '2023-01-01T00:00Z'
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


def generate_poisson_events(rate, time_duration):
    num_events = np.random.poisson(rate * (time_duration + 1))
    event_times = np.sort(np.random.uniform(0, time_duration + 1, num_events))
    inter_arrival_times = np.diff(event_times)
    return num_events, event_times, inter_arrival_times

def count_events(event_times, duration):
    i = 0
    j = 0
    events_at_slot_i = []
    while (i < duration):
        count_events = 0
        while event_times[j] < i + 1:
            count_events += 1
            j += 1
        events_at_slot_i.append(count_events)
        i = i + 1
    return events_at_slot_i

def generate_events(l, half_hours):
    _, event_times, _ = generate_poisson_events(l, 8)
    return count_events(event_times, 8)

def generate_event_trace(days, lambdas = [250, 100, 500, 250, 500, 1000]):
    events_at_slot_i = []

    for d in range(days):
        for j in range(6):
            events_at_slot_i += generate_events(lambdas[j], 8)
            
    return events_at_slot_i

print('### Generating events trace')

events_at_slot_i = generate_event_trace(days)

print('### Done!')


print('### Writing data to files')
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['time', 'actual', 'forecast', 'reqs'])
    for i in range(0, half_hours):
        writer.writerow([res[i]['from'], res[i]['intensity']['actual'], res[i]['intensity']['forecast'], events_at_slot_i[i]])

with open('input.lp', 'w') as inputfile:
    inputfile.write('timeSlot(1..'+str(half_hours)+').\n')
    inputfile.write('desiredPrecision(90).\n')

    inputfile.write('\n')
    inputfile.write('strategy(0, 1, 85).\nstrategy(1, 2, 92).\nstrategy(2, 3, 100).\n')
    inputfile.write('\n')

    for i in range(0, half_hours):
        inputfile.write('reqs('+str(i+1)+', '+str(events_at_slot_i[i])+').\n')
    
    inputfile.write('\n')
    
    for i in range(0, half_hours):
        inputfile.write('carbon('+str(i+1)+', '+str(res[i]['intensity']['forecast'])+').\n')

print('### Done!')