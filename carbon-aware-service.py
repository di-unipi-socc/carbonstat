from datetime import datetime
from enum import Enum
from flask import Flask,request,jsonify
from os import environ
import random

# Carbon intensity reader (mock)
from carbon.reader_mock import CarbonIntensityReader

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
        self.co2 = None
        self.highPowerLimit = float(environ["HIGHPOWER_LIMIT"])
        self.mediumPowerLimit = float(environ["MEDIUMPOWER_LIMIT"])
        startingCO2 = float(environ["STARTING_CO2"])
        stepCO2 = float(environ["CO2_STEP"])
        limitCO2 = float(environ["CO2_LIMIT"])
        self.carbonIntensityReader = CarbonIntensityReader(startingCO2,stepCO2,limitCO2)
     
    def getCarbonAwareStrategy(self,green) -> CarbonAwareStrategy:
        self.co2 = self.carbonIntensityReader.read()
        if green:
            if self.co2 > self.mediumPowerLimit:
                return CarbonAwareStrategies.LowPower.value
            elif self.co2 > self.highPowerLimit:
                return CarbonAwareStrategies.MediumPower.value
        return CarbonAwareStrategies.HighPower.value

# ------ SERVICE ------
app = Flask(__name__)

# app data
with open("data/numbers.txt","r") as numbers:
    values = numbers.read().split(",")
    app.data = [] 
    for val in values:
        app.data.append(int(val))
    random.shuffle(app.data)

# set service's context
app.context = Context()

@app.route("/")
def nop():
    # Parse params and check if forcing to not run approximated
    greenParameter = request.args.get("green")
    if greenParameter and greenParameter.lower() == "false":
        green = False
    else:
        green = True
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(green)
    # Invoke strategy with dynamic typing
    answer = strategy.nop() + "\n"
    return answer

@app.route("/avg")
def avg():
    # Parse params and check if forcing to not run approximated
    greenParameter = request.args.get("green")
    if greenParameter and greenParameter.lower() == "false":
        green = False
    else:
        green = True
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy(green)
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
    result["carbon"] = app.context.co2
    return jsonify(result)

app.run(host='0.0.0.0',port=50000)