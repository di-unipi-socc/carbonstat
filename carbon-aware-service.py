from datetime import datetime
from enum import Enum
from flask import Flask,request,jsonify
from os import environ

# Carbon intensity reader (mock)
from monitoring.mock import Monitor

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
        # high power strategy limits
        highLimits = environ["HIGH_POWER_LIMITS"].split(",")
        self.high = {}
        self.high["maxCarbon"] = int(highLimits[0])
        self.high["maxRequests"] = int(highLimits[1])
        # medium power strategy limits 
        mediumLimits = environ["MEDIUM_POWER_LIMITS"].split(",")
        self.medium = {}
        self.medium["maxCarbon"] = int(mediumLimits[0])
        self.medium["maxRequests"] = int(mediumLimits[1])
        # connection to monitoring 
        self.monitor = Monitor()
    
    # getter for carbon-aware strategy
    def getCarbonAwareStrategy(self,high) -> CarbonAwareStrategy:
        self.carbon = self.monitor.carbon()
        self.requests = self.monitor.requests()
        if high or (self.carbon <= self.high["maxCarbon"] and self.requests <= self.high["maxRequests"]):
            return CarbonAwareStrategies.HighPower.value
        elif self.carbon <= self.medium["maxCarbon"] and self.requests <= self.medium["maxRequests"]:
            return CarbonAwareStrategies.MediumPower.value
        return CarbonAwareStrategies.LowPower.value

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
    # Parse params and check if forcing to not run approximated
    forceParameter = request.args.get("force")
    force = forceParameter and (forceParameter.lower()=="true")
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(force)
    # Invoke strategy with dynamic typing
    answer = strategy.nop() + "\n"
    return answer

@app.route("/avg")
def avg():
    # Parse params and check if forcing to not run approximated
    forceParameter = request.args.get("force")
    force = forceParameter and (forceParameter.lower()=="true")
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(force)
    # Invoke strategy with dynamic typing (and measure running time)
    start = datetime.now()
    average = strategy.avg(app.data)
    end = datetime.now()
    elapsed = round((end.timestamp() - start.timestamp())*1000,2)
    # Return result and elapsed time
    result = {}
    result["value"] = average
    result["elapsed"] = elapsed
    result["strategy"] = strategy.nop()
    result["carbon"] = app.context.carbon
    return jsonify(result)

app.run(host='0.0.0.0',port=50000)