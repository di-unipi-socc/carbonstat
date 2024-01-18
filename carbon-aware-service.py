from datetime import datetime
from enum import Enum
from flask import Flask,request,jsonify
from os import environ

# ------ STRATEGIES ------
# Import and enum carbon-aware strategies (aka. flavours)
from flavours.interface import CarbonAwareStrategy
from flavours.low_power import LowPowerStrategy
from flavours.medium_power import MediumPowerStrategy
from flavours.high_power import HighPowerStrategy

class CarbonAwareStrategies(Enum):
    LowPower = LowPowerStrategy
    MediumPower = MediumPowerStrategy
    HighPower = HighPowerStrategy

# ------ CONTEXT ------
# Carbon-aware context
class Context:
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer
    def __init__(self):
        self.assignment = {}
        assignment = open(environ["ASSIGNMENT"])
        for a_line in list(assignment)[1:]:
            a = a_line.replace("\n","").split(",")
            hour = a[0]
            minute = a[1]
            strategy = a[2]
            self.assignment[hour+":"+minute] = CarbonAwareStrategies[strategy].value
        assignment.close()
    
    # getter for carbon-aware strategy
    def getCarbonAwareStrategy(self,force_strategy) -> CarbonAwareStrategy:
        if force_strategy is not None:
            return CarbonAwareStrategies[force_strategy].value
        now = datetime.now()
        if (now.minute < 30):
            return self.assignment[str(now.hour)+":0"]
        else:
            return self.assignment[str(now.hour)+":30"]

# ------ SERVICE ------
app = Flask(__name__)

# app data
with open("data/numbers.txt","r") as numbers:
    values = numbers.read().split(",")
    app.data = [] 
    for val in values:
        app.data.append(int(val))

# set service's context
app.context = Context()

@app.route("/")
def nop():
    # Parse params and check if forced to run a given strategy
    force_strategy = request.args.get("force")
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(force_strategy)
    # Invoke strategy with dynamic typing
    answer = strategy.nop() + "\n"
    return answer

@app.route("/avg")
def avg():
    # Parse params and check if forced to run a given strategy
    force_strategy = request.args.get("force")
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(force_strategy)
    # Invoke strategy with dynamic typing (and measure running time)
    start = datetime.now()
    average = strategy.avg(app.data)
    end = datetime.now()
    elapsed = round((end.timestamp() - start.timestamp())*1000,2) # in milliseconds
    # Return result and elapsed time
    result = {}
    result["value"] = average
    result["elapsed"] = elapsed
    result["strategy"] = strategy.nop()
    result["carbon"] = app.context.carbon
    return jsonify(result)

app.run(host='0.0.0.0',port=50000)