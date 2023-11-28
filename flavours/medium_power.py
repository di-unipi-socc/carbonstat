from flavours.interface import CarbonAwareStrategy

# Medium power strategy
class MediumPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "MEDIUM_POWER"

    def avg(data) -> float:
        sum = 0
        step = 100
        size = len(data)
        for i in range(0,size,step):
            sum += data[i]
        return sum*step/size