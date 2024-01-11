class CarbonIntensityReader():
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer (values are in grams of co2 per hour)
    def __init__(self,lowerbound,step,upperbound):
        self.co2 = self.lowerbound = lowerbound # co2 emissions of current epoch
        self.step = step
        self.direction = +1
        self.upperbound = upperbound
        self.requests = 0 # requests per epoch
    
    # mocked carbon emissions' reader
    def read(self) -> int:
        # keep track of "requests per epoch"
        self.requests += 1
        # update current value (sinusoid going from lowerbound to upperbound - and back, each time increasing/decreasing by step)
        if self.co2 <= self.lowerbound: 
            self.direction = +1
        if self.co2 >= self.upperbound: 
            self.direction = -1
        self.co2 += self.direction*self.step
        # TODO: return also current value of "requests per epoch"
        return self.co2