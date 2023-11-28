from flavours.interface import CarbonAwareStrategy

# Full power strategy
class FullPowerStrategy(CarbonAwareStrategy):
    
    def nop() -> str:
        return "FULL_POWER"
    
    def avg(data) -> float:
        sum = 0
        size = len(data)
        for i in range(0,size):
            sum += data[i]
        return sum/size