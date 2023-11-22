from flavours.interface import CarbonAwareStrategy

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):
    def op() -> str:
        return "Running low power..\n"
