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
days = 30
init_date = '2023-01-01T00:00Z'
clusters = 8
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
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['time', 'actual', 'forecast', 'reqs'])
    for i in range(0, half_hours):
        writer.writerow([res[i]['from'], res[i]['intensity']['actual'], res[i]['intensity']['forecast'], events_at_slot_i[i]])
        carbon.append(res[i]['intensity']['forecast'])

data = list(zip(carbon, events_at_slot_i))

kmeans = KMedoids(n_clusters=clusters)
kmeans.fit(data)

print(kmeans.cluster_centers_)

with open('input.lp', 'w') as inputfile:
    inputfile.write('timeSlot(1..'+str(clusters)+').\n')
    inputfile.write('maxError(6).\n')
    
    totReqs = sum(kmeans.cluster_centers_[:, 1])
    inputfile.write('totalReqs(' + str(int(totReqs)) + ').\n')

    inputfile.write('\n')
    inputfile.write('strategy(lowpower, 1, 15).\nstrategy(midpower, 2, 5).\nstrategy(hipower, 3, 0).\n')
    inputfile.write('\n')

    for i in range(0, clusters):
        inputfile.write('data('+ str(i+1) + ', ' +str(int(kmeans.cluster_centers_[i][0]/10)) + ', ' + str(int(kmeans.cluster_centers_[i][1]/10)) + ').\n')
                                                      
plt.scatter(carbon, events_at_slot_i, c = kmeans.labels_, cmap='rainbow')
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], color='black')
plt.show()

print('### Done!')