import requests
from argparse import ArgumentParser
from ortools.sat.python import cp_model

# function to import input data
def import_data(input_time_slots,input_strategies):
    # import time slots' data
    time_slots = open(input_time_slots)
    data = {}
    data["time_slots"] = []
    for line in list(time_slots)[1:]:
        values = line.replace("\n","").split(",")
        t = {}
        t["time_slot"] = values[0]
        t["carbon_actual"] = int(values[1])
        t["carbon_forecast"] = int(values[2])
        t["requests_actual"] = int(values[3])
        t["requests_forecast"] = int(float(values[4]))
        data["time_slots"].append(t)

    # import strategies' data
    data["strategies"] = []
    strategies = open(input_strategies)
    for line in list(strategies)[1:]:
        values = line.replace("\n","").split(",")
        s = {}
        s["strategy"] = values[0]
        s["elapsed_time"] = round(float(values[1]))
        s["error"] = round(float(values[2])*100) # considering up to 2 decimals (but as integers)
        data["strategies"].append(s)
    return data

# function to export output data
def export_assignment(assignment,data,output_assignment):
    output_csv = open(output_assignment,"w")
    output_csv.write("time_slot,strategy\n") #,carbon_actual,carbon_forecast,requests_actual,requests_forecast\n")
    for t in range(len(data["time_slots"])):
        output_csv.write(data["time_slots"][t]["time_slot"] + ",")
        output_csv.write(data["strategies"][assignment[t]]["strategy"] + "\n") #",")
        # output_csv.write(str(data["time_slots"][t]["carbon_actual"]) + ",")
        # output_csv.write(str(data["time_slots"][t]["carbon_forecast"]) + ",")
        # output_csv.write(str(data["time_slots"][t]["requests_actual"]) + ",")
        # output_csv.write(str(data["time_slots"][t]["requests_forecast"]) + "\n")

# function to compute emissions due to choosing a strategy for a time_slot
def emissions(strategy,time_slot,data):
    carbon = data["time_slots"][time_slot]["carbon_forecast"]
    requests = data["time_slots"][time_slot]["requests_forecast"]
    elapsed_time = data["strategies"][strategy]["elapsed_time"]
    return carbon * requests * elapsed_time

# class to collect the results returned by the CPModel
class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self,assignment,data):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = []
        # add all assignment's variables
        self.__assignment = assignment
        self.__data = data
        for t in range(len(data["time_slots"])):
            for s in range(len(data["strategies"])):
                self.__variables.append(assignment[(t,s)])
        self.__solution_list = []
    
    def on_solution_callback(self):
        new_solution = []
        for t in range(len(self.__data["time_slots"])):
            for s in range(len(self.__data["strategies"])):
                if self.Value(self.__assignment[(t,s)]):
                    new_solution.append(s)
        self.__solution_list.append(new_solution)
    
    def get_solutions(self):
        return self.__solution_list

# function to compute the emissions of a given assignment
def assignment_emissions(assignment, data):
    co2 = 0
    for t in range(len(data["time_slots"])):
        co2 += emissions(assignment[t],t,data)
    return co2

# function to compute average error of a given assignment
def assignment_error(assignment, data):
    avg_error = 0
    total_requests = 0
    for t in range(len(data["time_slots"])):
        requests = data["time_slots"][t]["requests_forecast"]
        s_error = data["strategies"][assignment[t]]["error"]
        avg_error += requests * s_error
        total_requests += requests
    return round((avg_error/total_requests)/100,5)
    
def main(input_time_slots,input_strategies,error_threshold,output_assignment):
    # get input data
    data = import_data(input_time_slots,input_strategies)

    # create model 
    model = cp_model.CpModel()

    # define variables (boolean variables representing the assignment of strategy s at time t)
    assignment = {}
    for t in range(len(data["time_slots"])):
        for s in range(len(data["strategies"])):
            assignment[(t,s)] = model.NewBoolVar(f"assignment_t{t}_s{s}")

    # constraint: exactly one strategy s at time t
    for t in range(len(data["time_slots"])):
        model.AddExactlyOne(assignment[(t,s)] for s in range(len(data["strategies"])))

    # constraint: average precision is at least data["precision_threshold"]
    error_threshold = error_threshold * 100 # modelling x% * 100
    max_weighted_error_threshold = 0
    for t in range(len(data["time_slots"])):
        max_weighted_error_threshold += data["time_slots"][t]["requests_forecast"] * error_threshold
    model.Add(max_weighted_error_threshold >= sum(
        assignment[(t,s)]*data["time_slots"][t]["requests_forecast"]*data["strategies"][s]["error"]
        for t in range(len(data["time_slots"]))
        for s in range(len(data["strategies"]))
    ))

    # objective: minimize emission
    model.Minimize(
        sum(
            assignment[(t,s)] * emissions(s,t,data)
            for t in range(len(data["time_slots"]))
            for s in range(len(data["strategies"]))
        )
    )

    # find all possible solutions for the modelled problem
    solver = cp_model.CpSolver()
    solution_collector = SolutionCollector(assignment,data)
    solver.parameters.enumerate_all_solutions = True
    status = solver.Solve(model,solution_collector)
    elapsed_time = solver.UserTime()

    # check if optimal solution was found
    if status != cp_model.OPTIMAL:
        print("No optimal solution found!")
        return 
    
    # pick the solution with the lowest emissions 
    # (if multiple solutions have the lowest emissions, pick that with lowest error)
    solutions = solution_collector.get_solutions() 
    best_solution = solutions[0] 
    best_emissions = assignment_emissions(best_solution,data)
    best_error = assignment_error(best_solution,data)
    for s in solutions[1:]:
        s_emissions = assignment_emissions(s,data)
        s_error = assignment_error(s,data)
        # print(s, s_emissions, s_error)
        if s_emissions < best_emissions or (s_emissions == best_emissions and s_error < best_error):
            best_solution = s
            best_emissions = s_emissions
            best_error = s_error

    export_assignment(best_solution,data,output_assignment)

    labeled_best_solution = []
    for s_index in best_solution:
        labeled_best_solution.append(data["strategies"][s_index]["strategy"])
    print("Best assignment:", labeled_best_solution)
    print("  - Emissions:", round(best_emissions/(3600*1000*1000),4),"gCO2/W")
    print("  - Average error:", round(best_error,4), "%")
    print("  - Solve time:", round(elapsed_time,4), "ms")

# ------------------------
#    RUN
# ------------------------ 
# Parse command-line arguments
parser = ArgumentParser("Optimizer of assignments of strategies to time slots")
parser.add_argument('input_time_slots', type=str, help='File with time slot data')
parser.add_argument('input_strategies', type=str, help='File with statistics on strategies')
parser.add_argument('error', type=int, help='Tolerated error (%)')
parser.add_argument('output_assignment', type=str, help='File where to write the output assignment')
args = parser.parse_args()

main(args.input_time_slots,args.input_strategies,int(args.error),args.output_assignment)