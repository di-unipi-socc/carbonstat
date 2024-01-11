from os import environ

class Monitor():
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer (values are in grams of co2 per hour)
    def __init__(self):
        self._carbon = int(environ["CARBON_INTENSITY"])
        self._requests = int(environ["REQUESTS"])
    
    # mocked reader of carbon intensity
    def carbon(self) -> int:
        return self._carbon
    
    # mocked reader of amount of requests
    def requests(self) -> int:
        return self._requests
