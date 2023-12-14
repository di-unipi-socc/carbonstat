from ortools.sat.python import cp_model
import time

# function to import input data
def import_data():
    # TODO: import data from csv?
    data = {}
    data["strategies"] = [0, 1, 2]
    data["s_time"] = [3, 2, 1]
    data["s_precision"] = [100, 90, 80]
    data["time"] = [0,1,2,3,4,5,6,7,8,9,10]
    data["rate"] = [3,4,5,2,1,6,7,2,5,6,7]
    data["carbon"] = [100,1000,5,200,1000,100,67,567,2,800,5]
    data["precision_threshold"] = 100
    return data

# function to compute the carbon emissions due to choosing a given strategy at a given time
def emissions(strategy,start_time,data):
    co2 = 0
    # determine end time based on service time and max possible time
    end_time = start_time + data["s_time"][strategy]
    max_time = len(data["time"])-1
    if (end_time > max_time):
        end_time = max_time

    # emissions for a single request
    for t in range(start_time,end_time):
        co2 += data["carbon"][t]
    # emissions for all requests at time "start_time"
    n_reqs = data["rate"][start_time]
    co2 *= n_reqs
    return co2

# class to collect the results returned by the CPModel
class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self,assignment,data):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = []
        # add all assignment's variables
        self.__assignment = assignment
        self.__data = data
        for s in data["strategies"]:
            for t in data["time"]:
                self.__variables.append(assignment[(s,t)])
        self.__solution_list = []
    
    def on_solution_callback(self):
        new_solution = []
        for t in self.__data["time"]:
            for s in self.__data["strategies"]:
                if self.Value(self.__assignment[(s,t)]):
                    new_solution.append(s)
        self.__solution_list.append(new_solution)
    
    def get_solutions(self):
        return self.__solution_list

# function to compute the precision of a given solution
def sol_precision(solution,data):
    # weighted average of precisions
    precision = 0
    total_queries = 0
    for t in data["time"]:
        s = solution[t]
        precision += data["s_precision"][s] * data["rate"][t]
        total_queries += data["rate"][t]
    return precision/total_queries

# function to compute the emissions of a given solution
def sol_emission(solution,data):
    e = 0
    for t in data["time"]:
        e += emissions(solution[t],t,data)
    return e

def main():
    # get input data
    data = import_data()

    # create model 
    model = cp_model.CpModel()

    # define variables (boolean variables representing the assignment of strategy s at time t)
    assignment = {}
    for s in data["strategies"]:
        for t in data["time"]:
            assignment[(s,t)] = model.NewBoolVar(f"assignment_s{s}_t{t}")

    # constraint: exactly one strategy s at time t
    for t in data["time"]:
        model.AddExactlyOne(assignment[(s,t)] for s in data["strategies"])

    # constraint: average precision is at least data["precision_threshold"]
    min_weighted_precision = 0
    for r in data["rate"]:
        min_weighted_precision += r * data["precision_threshold"]
    model.Add(min_weighted_precision <= sum(
        assignment[(s,t)]*data["s_precision"][s]*data["rate"][t]
        for s in data["strategies"]
        for t in data["time"]
    ))

    # constraint: assignment(s1,t1) and assignment(s2,t2) and s1<s2 => data["carbon"][t1] > data["carbon"][t2]
    for t1 in data["time"]:
        for t2 in data["time"]:
            for s1 in data["strategies"]:
                for s2 in data["strategies"]:
                    if (s1 < s2):
                        # create variable representing assignment(s1,t1) and assignment(s2,t2)
                        and_assignment = model.NewBoolVar("")
                        # assignment(s1,t1) and assignment(s2,t2) => and_assignment
                        # (rewritten as not(assignment(s1,t1) and assignment(s2,t2)) or and_assignment)
                        model.AddBoolOr([assignment[(s1,t1)].Not(), assignment[(s2,t2)].Not(), and_assignment])
                        # and_assignment => assignment(s1,t1) and assignment(s2,t2)
                        model.AddImplication(and_assignment,assignment[(s1,t1)])
                        model.AddImplication(and_assignment,assignment[(s2,t2)])
                        # add implication of and_assignment on carbon
                        model.AddImplication(and_assignment,data["carbon"][t1] < data["carbon"][t2])


    # objective: minimize emission
    model.Minimize(
        sum(
            assignment[(s,t)] * emissions(s,t,data)
            for s in data["strategies"] 
            for t in data["time"]
        )
    )

    # find all possible solutions for the modelled problem
    solver = cp_model.CpSolver()
    solution_collector = SolutionCollector(assignment,data)
    s_time = time.time()
    status = solver.SolveWithSolutionCallback(model,solution_collector)
    e_time = time.time()

    # check if problem can be solved
    if status != cp_model.OPTIMAL:
        print("No optimal solution found!")
        return 
    
    # DEBUG: print all found solutions
    for solution in solution_collector.get_solutions():
        print(solution)

    # pick the first solution with the highest precision
    max_precision = -1
    best_solution = None
    solutions = solution_collector.get_solutions() # array with indexes denoting times and values denoting chosen strategies
    for solution in solutions:
        p = sol_precision(solution,data)
        if p > max_precision:
            best_solution = solution
            max_precision = p 

    print("Solution:", best_solution)
    print("Emissions:", sol_emission(best_solution,data))
    print("Precision:", sol_precision(best_solution,data))
    print("Execution time:", (e_time - s_time))
    # TODO: Extract thresholds by analysing picked solution

main()