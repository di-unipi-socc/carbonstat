from datetime import datetime
from enum import Enum
from flask import Flask

# Carbon intensity reader (mock)
from carbon.reader_mock import CarbonIntensityReader

# ------ STRATEGIES ------
# Import and enum carbon-aware strategies (aka. flavours)
from flavours.interface import CarbonAwareStrategy
from flavours.low_power import LowPowerStrategy
from flavours.full_power import FullPowerStrategy

class CarbonAwareStrategies(Enum):
    LowPower = LowPowerStrategy
    FullPower = FullPowerStrategy

# ------ CONTEXT ------
# Carbon-aware context
class Context:
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer
    def __init__(self):
        self.carbonIntensityReader = CarbonIntensityReader(100,500,1500)
     
    def getCarbonAwareStrategy(self) -> CarbonAwareStrategy:
        co2 = self.carbonIntensityReader.read()
        print(co2)
        if (co2 >= 1000):
            return CarbonAwareStrategies.LowPower.value
        else:
            return CarbonAwareStrategies.FullPower.value

# ------ SERVICE ------
app = Flask(__name__)
app.context = Context()

@app.route("/")
def op():
    # TODO: add parameter extraction here, when needed
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy()
    # Invoke strategy with dynamic typing
    answer = strategy.op()
    return answer

app.run(host='0.0.0.0',port=50000)