import os
from requests import get
from time import sleep

# function to process policy results
def update(policyResult,getReply):
    policyResult["values"].append(float(getReply["average"]))
    policyResult["carbon"] += float(getReply["carbon"])*float(getReply["elapsed"])/1000 # assuming carbon per second, elapsed in millisecond
def process(policyResult,referenceValue):
    values = policyResult.pop("values")
    policyResult["queries"] = len(values)
    avg = 0
    for val in values: 
        avg += val
    avg = avg / len(values)
    policyResult["average"] = avg
    if (referenceValue is not None):
        deviation = abs(avg - referenceValue)
        policyResult["precision"] = 100 - round(deviation/referenceValue*100,2)
    else:
        policyResult["precision"] = 100

# experiment configuration
queries = 10000
experimentSize = "1000000"
carbonMock = { "start": "100", "step": "500", "limit": "3100"}
policies = [
    { "name": "wasting", "fullPowerLimit": "1500", "mediumPowerLimit": "2500"}, 
    { "name": "balanced", "fullPowerLimit": "1000", "mediumPowerLimit": "2000"}, 
    { "name": "saving", "fullPowerLimit": "500", "mediumPowerLimit": "1000"}, 
]

# clean result file
os.system("rm results.txt")

# run experiment
for policy in policies:
    # config experiment template
    template = open("experiment-template.yml") 
    experiment = template.read()
    template.close()
    experiment = experiment.replace("CO2START",carbonMock["start"])
    experiment = experiment.replace("CO2STEP",carbonMock["step"])
    experiment = experiment.replace("CO2LIMIT",carbonMock["limit"])
    experiment = experiment.replace("FPLIMIT",policy["fullPowerLimit"])
    experiment = experiment.replace("MPLIMIT",policy["mediumPowerLimit"])
    experiment = experiment.replace("EXPSIZE",experimentSize)
    with (open("experiment-deploy.yml","w")) as experimentDeploy: 
        experimentDeploy.write(experiment)
    
    # build and deploy experiment
    os.system("docker-compose -f experiment-deploy.yml build")
    os.system("docker-compose -f experiment-deploy.yml up &")
    sleep(10)
    
    # send queries and collect results
    policyResult = {}
    policyResult["low"] = { "values": [], "carbon": 0 }
    policyResult["medium"] = { "values": [], "carbon": 0 }
    policyResult["high"] = { "values": [], "carbon": 0 }
    for i in range(queries):
        getReply = get("http://127.0.0.1:50000/avg").json()
        if "LOW" in getReply["strategy"]:
            update(policyResult["low"],getReply)
        elif "MEDIUM" in getReply["strategy"]:
            update(policyResult["medium"],getReply)
        else:
            update(policyResult["high"],getReply)
    
    # undeploy experiment
    os.system("docker-compose -f experiment-deploy.yml down")

    # process queries' results
    process(policyResult["high"],None)
    process(policyResult["medium"],policyResult["high"]["average"])
    process(policyResult["low"],policyResult["high"]["average"])

    with open("results.txt","a") as results:
        results.write(policy["name"] + "\n")
        results.write("High: " + str(policyResult["high"]) + "\n")
        results.write("Medium: " + str(policyResult["medium"]) + "\n")
        results.write("Low: " + str(policyResult["low"]) + "\n")