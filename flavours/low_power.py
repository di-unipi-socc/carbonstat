from flavours.interface import CarbonAwareStrategy

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "LOW_POWER"

    def avg(data) -> float:
        sum = 0
        step = 10000
        size = len(data)
        for i in range(0,size,step):
            sum += data[i]
        return sum*step/size