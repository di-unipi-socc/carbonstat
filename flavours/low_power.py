from flavours.interface import CarbonAwareStrategy

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):

    def nop() -> str:
        return "LOW_POWER"

    def avg(data) -> float:
        sum = 0
        # consider 1 number every square_root(len(data))
        step = round((len(data))**(1/2))
        # compute avg 
        count = 0
        size = len(data)
        for i in range(0,size,step):
            count += 1
            sum += data[i]
        return sum/count