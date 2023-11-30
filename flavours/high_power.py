from flavours.interface import CarbonAwareStrategy

# High power strategy
class HighPowerStrategy(CarbonAwareStrategy):
    
    def nop() -> str:
        return "HIGH_POWER"
    
    def avg(data) -> float:
        sum = 0
        size = len(data)
        for i in range(0,size):
            sum += data[i]
        return round(sum/size)