import requests
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import csv
import numpy as np



# Specify the interval of days and the initial date
days = 1
init_date = '2023-01-01T00:00Z'
###################################################


half_hours = 48 * days
delta = timedelta(days = days, hours= 0, minutes= 0)

fr = parser.parse(init_date)
to = fr + delta

headers = {
  'Accept': 'application/json'
}
url = 'https://api.carbonintensity.org.uk/intensity/' + fr.isoformat() + '/' + to.isoformat()
 
r = requests.get(url, params={}, headers = headers)
 
#print(str(r.json()).replace("'", '"'))

res = dict(r.json())['data']

def generate_poisson_events(rate, time_duration):
    num_events = np.random.poisson(rate * time_duration)
    event_times = np.sort(np.random.uniform(0, time_duration, num_events))
    inter_arrival_times = np.diff(event_times)
    return num_events, event_times, inter_arrival_times

_, event_times, _ = generate_poisson_events(1000, half_hours)


events_at_slot_i = []

i = 0
j = 0
while (i < half_hours):
    count_events = 0
    while event_times[j] < i:
        count_events += 1
        j += 1
    events_at_slot_i.append(count_events)
    i = i + 1


    
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['time', 'actual', 'forecast', 'reqs'])
    for i in range(0, half_hours):
        writer.writerow([res[i]['from'], res[i]['intensity']['actual'], res[i]['intensity']['forecast'], events_at_slot_i[i]])
