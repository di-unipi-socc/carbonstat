import os
from requests import get
from time import sleep

# function to update (ongoing) policy results
def update(policyResult,getReply):
    policyResult["values"].append(float(getReply["value"]))
    # measure carbon emission considering carbon intensity, elapsed time, and power consumption
    carbonIntensity = float(getReply["carbon"])*1000 # mg of co2-eq/(kW*h)
    elapsedTime = float(getReply["elapsed"])/(3600*1000) # elapsed hours for computation (h)
    power = 0.05 # worst-case power consumption of my laptop(kW) 
    policyResult["carbon"] += carbonIntensity * power * elapsedTime

# function to post-process policy results (measuring precision against a ref value)
def process(policyResult,referenceValue):
    # remove returned values
    values = policyResult.pop("values")
    # round carbon emission
    policyResult["carbon"] = round(policyResult["carbon"],2)
    # count how many queries were done
    policyResult["queries"] = len(values)
    # compute average of returned values
    avg = 0
    if len(values) > 0: 
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
repetitions = 10
queries = 1000
carbonMock = { "start": "5", "step": "20", "limit": "1100"} # from (solar) 5g to (coal) 1100g of CO2-eq/kWh
policies = [
    { "name": "carbon-unaware", "highPowerLimit": "2000", "mediumPowerLimit": "2100"},
    { "name": "super-power-hungry", "highPowerLimit": "850", "mediumPowerLimit": "1000"}, 
    { "name": "power-hungry", "highPowerLimit": "750", "mediumPowerLimit": "950"}, 
    { "name": "balanced", "highPowerLimit": "350", "mediumPowerLimit": "750"}, 
    { "name": "saving", "highPowerLimit": "150", "mediumPowerLimit": "350"}, 
    { "name": "super-saving", "highPowerLimit": "100", "mediumPowerLimit": "250"}, 
]

# clean result and log file (if any)
os.system("rm results.txt 2>/dev/null")
os.system("rm log.txt 2>/dev/null")

logFile = open("exp.log",mode="w",buffering=1)

iterations = []
for i in range(repetitions):
    logFile.write("\nITERATION: " + str(i) + "\n")
    
    # force re-build of image, to re-create dataset
    logFile.write("|- Building Docker image...")
    os.system("docker compose -f experiment-template.yml build --no-cache >> log.txt 2>> log.txt")
    logFile.write("done!\n")

    # run i-th experiment
    ithResult = {}
    iterations.append(ithResult)
    for policy in policies:
        policyName = policy["name"]
        logFile.write("|- Policy: " + policyName + "\n")

        # config experiment's deployment (from template)
        template = open("experiment-template.yml") 
        experiment = template.read()
        template.close()
        experiment = experiment.replace("CO2START",carbonMock["start"])
        experiment = experiment.replace("CO2STEP",carbonMock["step"])
        experiment = experiment.replace("CO2LIMIT",carbonMock["limit"])
        experiment = experiment.replace("HPLIMIT",policy["highPowerLimit"])
        experiment = experiment.replace("MPLIMIT",policy["mediumPowerLimit"])
        with (open("experiment-deploy.yml","w")) as experimentDeploy: 
            experimentDeploy.write(experiment)
        
        # deploy configured experiment
        logFile.write("|  |- Deploying carbon-aware service...")
        os.system("docker compose -f experiment-deploy.yml up -d >> log.txt 2>> log.txt")
        sleep(10)
        logFile.write("done!\n")

        # send queries and collect results
        logFile.write("|  |- Sending queries...")
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
        logFile.write("done!\n")

        # undeploy experiment
        logFile.write("|  |- Undeploying carbon-aware service...")
        os.system("docker compose -f experiment-deploy.yml down 2>> log.txt")
        logFile.write("done!\n")

        # process queries' results and append them to collection of results
        logFile.write("|  |- Post processing results...")
        process(ithResult[policyName]["high"],None)
        process(ithResult[policyName]["medium"],ithResult[policyName]["high"]["average"])
        process(ithResult[policyName]["low"],ithResult[policyName]["high"]["average"])
        logFile.write("done!\n")

    # end of iteration
    logFile.write("|- End of iteration\n")

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

logFile.write("\n COMPLETED")
logFile.close()