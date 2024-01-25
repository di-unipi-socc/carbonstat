from flavours.interface import CarbonAwareStrategy
import random

# Medium power strategy
class MediumPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "MEDIUM_POWER"

    def avg(data) -> float:
        sum = 0
        # step set to consider 50% of the data
        step = 2
        # compute avg 
        count = 0
        size = len(data)
        for i in range(0,size,step):
            count += 1
            sum += data[i]
        return round(sum/count)