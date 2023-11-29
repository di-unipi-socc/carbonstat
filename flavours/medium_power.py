from flavours.interface import CarbonAwareStrategy

# Medium power strategy
class MediumPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "MEDIUM_POWER"

    def avg(data) -> float:
        sum = 0
        # consider 1 number every 1000
        step = 1000
        # compute avg 
        count = 0
        size = len(data)
        for i in range(0,size,step):
            count += 1
            sum += data[i]
        return sum/count