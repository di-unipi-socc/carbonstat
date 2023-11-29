import json
import os
from requests import get
from time import sleep

# function to process policy results
def update(policyResult,getReply):
    policyResult["values"].append(float(getReply["value"]))
    policyResult["carbon"] += float(getReply["carbon"])*float(getReply["elapsed"])/1000 # assuming carbon per second, elapsed in millisecond
def process(policyResult,referenceValue):
    # remove returned values
    values = policyResult.pop("values")
    # round carbon emission
    policyResult["carbon"] = round(policyResult["carbon"],2)
    # count how many queries were done
    policyResult["queries"] = len(values)
    # compute average of returned values
    avg = 0
    for val in values: 
        avg += val
    avg = avg / len(values)
    policyResult["average"] = round(avg,2)
    # compute precision (approx vs actual average)
    if (referenceValue is not None):
        deviation = abs(avg - referenceValue)
        policyResult["precision"] = 100 - round(deviation/referenceValue*100,2)
    else:
        policyResult["precision"] = 100

# experiment configuration
repetitions = 5
queries = 1000
carbonMock = { "start": "0", "step": "200", "limit": "3000"}
policies = [
    { "name": "super-power-hungry", "fullPowerLimit": "2000", "mediumPowerLimit": "2800"}, 
    { "name": "power-hungry", "fullPowerLimit": "1500", "mediumPowerLimit": "2500"}, 
    { "name": "balanced", "fullPowerLimit": "1000", "mediumPowerLimit": "2000"}, 
    { "name": "saving", "fullPowerLimit": "500", "mediumPowerLimit": "1500"}, 
    { "name": "super-saving", "fullPowerLimit": "200", "mediumPowerLimit": "1000"}, 
]

# clean result file (if any)
os.system("rm results.txt 2>/dev/null")

iterations = []
for i in range(repetitions):

    print("*** ITERATION: " + str(i) + " ***")
    ithResult = {}
    iterations.append(ithResult)

    # run i-th experiment
    for policy in policies:
        policyName = policy["name"]
        print("Policy: " + policyName)

        # config experiment's deployment (from template)
        template = open("experiment-template.yml") 
        experiment = template.read()
        template.close()
        experiment = experiment.replace("CO2START",carbonMock["start"])
        experiment = experiment.replace("CO2STEP",carbonMock["step"])
        experiment = experiment.replace("CO2LIMIT",carbonMock["limit"])
        experiment = experiment.replace("FPLIMIT",policy["fullPowerLimit"])
        experiment = experiment.replace("MPLIMIT",policy["mediumPowerLimit"])
        with (open("experiment-deploy.yml","w")) as experimentDeploy: 
            experimentDeploy.write(experiment)
        print("- Compose file built")
        
        # build and deploy experiment
        os.system("docker compose -f experiment-deploy.yml build > log.txt 2> log.txt")
        os.system("docker compose -f experiment-deploy.yml up -d > log.txt 2> log.txt")
        sleep(10)
        print("- Application up and running")

        # send queries and collect results
        ithResult[policyName] = {}
        ithResult[policyName]["low"] = { "values": [], "carbon": 0 }
        ithResult[policyName]["medium"] = { "values": [], "carbon": 0 }
        ithResult[policyName]["high"] = { "values": [], "carbon": 0 }
        for i in range(queries):
            getReply = get("http://127.0.0.1:50000/avg").json()
            if "LOW" in getReply["strategy"]:
                update(ithResult[policyName]["low"],getReply)
            elif "MEDIUM" in getReply["strategy"]:
                update(ithResult[policyName]["medium"],getReply)
            else:
                update(ithResult[policyName]["high"],getReply)
        print("- All queries sent")

        # undeploy experiment
        os.system("docker compose -f experiment-deploy.yml down > log.txt 2> log.txt")
        print("- Application undeployed")

        # process queries' results and append them to collection of results
        process(ithResult[policyName]["high"],None)
        process(ithResult[policyName]["medium"],ithResult[policyName]["high"]["average"])
        process(ithResult[policyName]["low"],ithResult[policyName]["high"]["average"])
        print("- Post-processing completed")

# combine results from different iterations
overallResult = {}
for ithResult in iterations:
    for policy in ithResult:
        if policy not in overallResult: 
            overallResult[policy] = {}
            overallResult[policy]["low"] = { "carbon": 0, "queries": 0, "precision": 0 }
            overallResult[policy]["medium"] = { "carbon": 0, "queries": 0, "precision": 0 }
            overallResult[policy]["high"] = { "carbon": 0, "queries": 0, "precision": 0 }
        for flavour in ithResult[policy]:
            overallResult[policy][flavour]["carbon"] += ithResult[policy][flavour]["carbon"]
            overallResult[policy][flavour]["queries"] += ithResult[policy][flavour]["queries"]
            overallResult[policy][flavour]["precision"] += ithResult[policy][flavour]["precision"]

for policy in overallResult:
    for flavour in overallResult[policy]:
        for key in overallResult[policy][flavour]:
            overallResult[policy][flavour][key] = round(overallResult[policy][flavour][key]/repetitions,2) 
    
# output overall results   
with open("results.txt","a") as results:
    for policy in overallResult:
        results.write(policy + "\n")
        for flavour in overallResult[policy]:
            results.write(flavour + " > " + str(overallResult[policy][flavour]) + "\n")

# clean useless logs
os.system("rm logs.txt")