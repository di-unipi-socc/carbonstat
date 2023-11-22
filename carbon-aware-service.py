from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from flask import Flask

# ------ STRATEGIES ------
# Abstract carbon-aware strategy
class CarbonAwareStrategy(ABC):
    @abstractmethod
    def get() -> str:
        pass

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):
    def get() -> str:
        return "Running low power.."

# Full power strategy
class FullPowerStrategy(CarbonAwareStrategy):
    def get() -> str:
        return "Running full power!!"

# Enum the supported carbon-aware strategies
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