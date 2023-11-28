from flavours.interface import CarbonAwareStrategy
from numpy import random

# Medium power strategy
class MediumPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "MEDIUM_POWER"

    def avg(data) -> float:
        sum = 0
        # consider 1 number every 100
        step = 100
        # set random starting point from 0 to step
        start = round(random.Generator(random.PCG64()).random()*step)
        # compute avg 
        count = 0
        size = len(data)
        for i in range(start,size,step):
            count += 1
            sum += data[i]
        return sum/count