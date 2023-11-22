from flavours.interface import CarbonAwareStrategy

# Full power strategy
class FullPowerStrategy(CarbonAwareStrategy):
    def get() -> str:
        return "Running full power!!"