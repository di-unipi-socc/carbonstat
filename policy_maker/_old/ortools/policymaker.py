from ortools.sat.python import cp_model

input_time_slots = "time_slots.csv"
input_strategies = "strategies.csv"

# function to import input data
def import_data():
    # import time slots' data
    time_slots = open(input_time_slots)
    data = {}
    data["time_slots"] = []
    for line in list(time_slots)[1:]:
        values = line.replace("\n","").split(",")
        t = {}
        t["time_slot"] = values[0]
        t["carbon"] = int(values[1])
        t["requests"] = int(values[2])
        data["time_slots"].append(t)

    # import strategies' data
    data["strategies"] = []
    strategies = open(input_strategies)
    for line in list(strategies)[1:]:
        values = line.replace("\n","").split(",")
        s = {}
        s["strategy"] = values[0]
        s["elapsed_time"] = round(float(values[1])) # *10)
        s["error"] = round(float(values[2])*10)
        data["strategies"].append(s)
    return data

# function to compute emissions due to choosing a strategy for a time_slot
def emissions(strategy,time_slot,data):
    carbon = data["time_slots"][time_slot]["carbon"]
    requests = data["time_slots"][time_slot]["requests"]
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
        requests = data["time_slots"][t]["requests"]
        s_error = data["strategies"][assignment[t]]["error"]
        avg_error += requests * s_error
        total_requests += requests
    return round((avg_error/total_requests)/10,5)
    
def main():
    # get input data
    data = import_data()
    # # DEBUG: print imported data
    # print(data)

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
    error_threshold = 50 # modelling 5.0% * 10
    max_weighted_error_threshold = 0
    for t in range(len(data["time_slots"])):
        max_weighted_error_threshold += data["time_slots"][t]["requests"] * error_threshold
    model.Add(max_weighted_error_threshold >= sum(
        assignment[(t,s)]*data["time_slots"][t]["requests"]*data["strategies"][s]["error"]
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
    status = solver.Solve(model,solution_collector)
    elapsed_time = solver.UserTime()

    # check if problem can be solved
    if status != cp_model.OPTIMAL:
        print("No optimal solution found!")
        return 
    
    # # DEBUG: print all found solutions
    # for solution in solution_collector.get_solutions():
    #     print("solution:", solution)
    #     print("co2:", assignment_emissions(solution,data))
    #     print("error:",assignment_error(solution,data))
    #     print("")
    # print("Execution time:", elapsed_time)

    # pick the solution with lowest emissions 
    solutions = solution_collector.get_solutions() 
    best_solution = solutions[-1] # solver is such that last solution is the best
    best_emissions = assignment_emissions(best_solution,data)
    best_error = assignment_error(best_solution,data)

    print("BEST:", best_solution)
    print("co2:", best_emissions)
    print("error:", best_error)

    output_csv = open("assignment.csv","w")
    output_csv.write("time_slot,strategy\n")
    for t in range(len(data["time_slots"])):
        output_csv.write(data["time_slots"][t]["time_slot"] + ",")
        output_csv.write(data["strategies"][best_solution[t]]["strategy"] + "\n")

main()