from flavours.interface import CarbonAwareStrategy

# Full power strategy
class FullPowerStrategy(CarbonAwareStrategy):
    def op() -> str:
        return "Running full power!!\n"