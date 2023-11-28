class CarbonIntensityReader():
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer (values are in grams of co2 per hour)
    def __init__(self,lowerbound,step,upperbound):
        self.co2 = self.lowerbound = lowerbound
        self.step = step
        self.direction = +1
        self.upperbound = upperbound
    
    # mocked carbon emissions' reader
    def read(self) -> int:
        # get current value
        co2 = self.co2 
        # update current value (sinusoid going from lowerbound to upperbound - and back, each time increasing/decreasing by step)
        if self.co2 <= self.lowerbound: 
            self.direction = +1
        if self.co2 >= self.upperbound: 
            self.direction = -1
        self.co2 += self.direction*self.step
        return self.co2