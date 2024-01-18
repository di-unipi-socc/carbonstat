import os 
from requests import get
from time import sleep

# ------------------------
#   CONFIG
# ------------------------
# Config data
reqs = 50
iterations = 20
totalReqs = reqs * iterations

strategies = ["HighPower","MediumPower","LowPower"]

# Clean logs
os.system("rm log.txt")

# ------------------------
#   RUN
# ------------------------
# Create data collectors
times = {}
errors = {}
for s in strategies:
    times[s] = 0
    errors[s] = 0

# Run queries 
for i in range(iterations):
    print("iteration: ",i)
    # force re-build of image to re-create dataset
    os.system("docker rmi carbon-aware-service >> log.txt 2>> log.txt")
    os.system("docker compose build >> log.txt 2>> log.txt")

    # deploy service
    os.system("docker compose up -d >> log.txt 2>> log.txt")
                
    # force high power call to get correct result
    correct_avg = None
    while correct_avg is None:
        sleep(1)
        try: 
            response = get("http://127.0.0.1:50000/avg?force=HighPower").json()
            correct_avg = float(response["value"])
        except:
            continue
    
    # for each available strategy
    for s in strategies:
        for r in range(reqs):
            print("  strategy:", s," req: ", r)
            response = get("http://127.0.0.1:50000/avg?force="+s).json()
            # sum elapsed time
            times[s] += round(float(response["elapsed"]),2)
            # sum error
            deviation = abs(float(response["value"]) - correct_avg)
            errors[s] = round(deviation/correct_avg*100,2)
            

    # undeploy service
    os.system("docker compose down >> log.txt 2>> log.txt")

# Determine avg time and error
for s in strategies:
    times[s] = round(times[s]/totalReqs,2)
    errors[s] = round(errors[s]/totalReqs,2)

# Write results on file
results = open("results.csv","w")
results.write("strategy,duration,error\n")
for s in strategies:
    results.write(s + ",")
    results.write(str(times[s]) + ",")
    results.write(str(errors[s]) + "\n")