# ------------------------
#    UTILITY 
# ------------------------
# TODO
# write function to compute emissions from elapsed time

# ------------------------
#    CONFIG 
# ------------------------
# Config data
power_consumption = 0.05 # worst-case power consumption of my laptop(kW) 

# TODO
# output csv file (timestamp,requests,iteration,policy,max_error,avg_error,avg_time,emissions)

# ------------------------
#    SIMULATORS 
# ------------------------

# ALWAYS HIGH/MEDIUM/LOW SIMULATOR
# Function to simulate the execution of the "always_high" policy
def run_always_high(carbon,requests):
    return run_always("HighPower",carbon,requests) 
# Function to simulate the execution of the "always_medium" policy
def run_always_medium(carbon,requests):
    return run_always("MediumPower",carbon,requests) 
# Function to simulate the execution of the "always_low" policy
def run_always_low(carbon,requests):
    return run_always("LowPower",carbon,requests) 
# Function to simulate the execution of the "always_s" policy, with strategy s passed as input
def run_always(s,carbon,requests):
    # TODO
    return

# NAIVE POLICY SIMULATOR
# Function to determine the strategy assigned to a timeslot by a naive policy
def naive_strategy(carbon,requests) -> str:
    if carbon < 110 and requests < 330:
        return "HighPower"
    elif carbon < 200 and requests < 660: 
        return "MediumPower"
    else: 
        return "LowPower"
# Function to simulate the execution of the "naive" policy
def run_naive(carbon,requests):
    # TODO
    return

# CARBOSTATE SIMULATOR
# Function to simulate the execution of the "carbostate" policy
def run_carbostate(carbon,requests):
    # TODO
    return

# ------------------------
#    RUN 
# ------------------------
# TODO: write the run for a single iteration, then use a sh script to run multiple iterations and then post-process outputs
"""
    for each timestamp:
        build docker image
        get true avg value
        run all queries for always_high and write avg error/time on csv
        run all queries for always_medium and write avg error/time on csv
        run all queries for always_low and write avg error/time on csv
        run all queries for naive and write avg error/time on csv
        run all queries for carbostate and write avg error/time on csv
    
    (( enable starting experiment from given timestamp, writing on csv output in append ))
"""