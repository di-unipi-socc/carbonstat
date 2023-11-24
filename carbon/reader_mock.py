class CarbonIntensityReader():
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer (values are in grams of co2 per hour)
    def __init__(self,startingValue,increaseValue,limitValue):
        self.co2 = startingValue
        self.step = increaseValue
        self.limit = limitValue
    
    # mocked periodic carbon emissions 
    def read(self) -> int:
        co2 = self.co2
        self.co2 = (self.co2 + self.step) % self.limit
        return co2