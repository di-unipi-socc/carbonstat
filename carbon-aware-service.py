from datetime import datetime
from enum import Enum
from flask import Flask

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
    def getCarbonAwareStrategy() -> CarbonAwareStrategy:
        # TODO: currently mocking co2 with a time check; to be fixed
        current = datetime.now().second
        if (current % 3 == 0):
            return CarbonAwareStrategies.LowPower.value
        else:
            return CarbonAwareStrategies.FullPower.value

# ------ SERVICE ------
app = Flask(__name__)

@app.route("/get")
def get():
    # TODO: add parameter extraction here, when needed
    # Get carbon-aware strategy
    strategy = Context.getCarbonAwareStrategy()
    # Invoke strategy with dynamic typing
    answer = strategy.get()
    return answer

app.run(host='0.0.0.0',port=50000)