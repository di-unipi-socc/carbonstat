from flavours.interface import CarbonAwareStrategy

# Full power strategy
class FullPowerStrategy(CarbonAwareStrategy):
    
    def nop() -> str:
        return "Running full power!!\n"
    
    def avg(data) -> float:
        sum = 0
        size = len(data)
        for i in range(0,size):
            sum += data[i]
        return sum/size