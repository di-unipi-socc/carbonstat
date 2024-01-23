from clyngor import ASP, solve

def solving(main, input):
    programs = [main, input]
    clasp_options = '--opt-mode=optN', '--parallel-mode=16', '--project', '--time-limit=900'
    answers = solve(programs, options=clasp_options, stats=True)
    print("solver run as: `{}`".format(answers.command))
    for answerset in answers.with_optimality.as_pyasp:
        yield answerset

answers = solving('pm.pl', 'input.lp')

loaded = []
foundOpt = False

for (a, (c1,c2), optimal) in answers:
    loaded.append((c1,c2,a,optimal))

    if optimal:
        print("Optimal solution found:")
        print(c1,c2,a,optimal)
        foundOpt = True
        break

if not foundOpt:
    print("No optimal solution found, printing best solution:")
    loaded = sorted(loaded)
