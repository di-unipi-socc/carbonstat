from flavours.interface import CarbonAwareStrategy
from numpy import random

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "LOW_POWER"

    def avg(data) -> float:
        sum = 0
        # consider 1 number every 10000
        step = 10000
        # set random starting point from 0 to step
        start = round(random.Generator(random.PCG64()).random()*step)
        # compute avg 
        count = 0
        size = len(data)
        for i in range(start,size,step):
            count += 1
            sum += data[i]
        return sum/count