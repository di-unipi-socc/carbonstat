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
days = 12
init_date = '2023-01-28T00:30Z'
asp_time_limit = 300 # seconds
max_error = 50 # percentage
rnd.seed(42+max_error) # for reproducibility
###################################################

for day in range(days):

    half_hours = 48
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

    with open('./traces_err'+str(max_error)+'/input/input'+str(day)+'.lp', 'w') as inputfile:
        # TODO: make error vary in [1, 5, 10] 
        inputfile.write('maxError('+str(max_error)+').\n')
        
        inputfile.write('\n')
        inputfile.write('strategy("LowPower", 36, 134).\nstrategy("MediumPower", 67, 45).\nstrategy("HighPower", 101, 0).\n')
        inputfile.write('\n')

        for i in range(0, half_hours):
            #inputfile.write('timeslot(' + str(i+1) + ', ' + str(round(res[i]['intensity']['forecast'])) + ', ' + str(round(events_at_slot_i[i])) + ').\n')
            inputfile.write('timeslot(' + str(i+1) + ', ' + str(round(res[i]['intensity']['forecast']/3.6)) + ', ' + str(round(events_at_slot_i[i]/100)) + ').\n')
                                       
    print('### Done!')

    from clyngor import ASP, solve

    def solving(main, input):
        programs = [main, input]
        clasp_options = '--opt-mode=optN', '--project', '--time-limit='+str(asp_time_limit) ,'--parallel-mode=8'
        answers = solve(programs, options=clasp_options, stats=True)
        print("solver run as: `{}`".format(answers.command))
        for answerset in answers.with_optimality: 
            yield answerset

    answers = solving('policy_maker.pl', './traces_err'+str(max_error)+'/input/input'+str(day)+'.lp')

    foundOpt = False
    carbostate, emissions, error = None, None, None

    for (a, (c1, c2), opt) in answers:
        carbostate = a
        emissions = c1
        error = c2
        foundOpt = opt

        if foundOpt:
            print("Optimal solution found")
            foundOpt = True
            break

    if not foundOpt:
        print("No optimal solution found")

    timeslots = []
    for strategy in carbostate:
        timeslots.append(strategy[1])

    sorted_timeslots = sorted(timeslots)

    strategies = []

    for (i,s) in sorted_timeslots:
        strategies.append(s.replace('"', ''))


    print('### Writing data to files')
    with open('./traces_err'+str(max_error)+'/data'+str(day)+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['time', 'strategy', 'actual_carbon', 'forecast_carbon', 'actual_reqs', 'forecast_reqs'])
        for i in range(0, half_hours):
            writer.writerow([res[i]['from'], strategies[i], res[i]['intensity']['actual'], res[i]['intensity']['forecast'], int(events_at_slot_i[i]+events_at_slot_i[i]*rnd.uniform(-0.05,0.05)), events_at_slot_i[i]])

        writer.writerow(['init_date', init_date])  
        writer.writerow(['emissions', emissions])
        writer.writerow(['error', error])
        if foundOpt:
            writer.writerow(['optimal', 'true'])

    # add four weeks to init_date
    init_date = (parser.parse(init_date) + timedelta(days=28)).isoformat()