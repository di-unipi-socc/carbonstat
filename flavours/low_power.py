from flavours.interface import CarbonAwareStrategy

# Low power strategy
class LowPowerStrategy(CarbonAwareStrategy):
    def get() -> str:
        return "Running low power.."
