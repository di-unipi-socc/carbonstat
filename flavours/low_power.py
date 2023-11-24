from flavours.interface import CarbonAwareStrategy

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "Running low power..\n"

    def avg(data) -> float:
        sum = 0
        step = 20
        size = len(data)
        for i in range(0,size,step):
            sum += data[i]
        return sum*step/size