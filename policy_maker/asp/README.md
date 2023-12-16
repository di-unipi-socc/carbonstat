# ASP Policymaker

This version of the policymaker employs Answer Set Programming. It relies on the [clingo](https://potassco.org/clingo/) grounder and solver.

## Knowledge Representation

Users just need to specify ground domains for:

- the considered time instants, i.e.  ` time(MinTime..MaxTime).`, 
- the number of strategies they consider, i.e.  `strategy(0..2).`, and 
- the time duration of the considered strategies, `duration(1..3).`.

Also, a fact `maxTime(MaxTime)` is needed.

Then, users can specify the characteristics of their strategies via facts like

```prolog
strategy(Id, TimeDuration, Precision).
```

where `Id` is the unique integer identifier for the strategy, `TimeDuration` its execution time in number of epochs, and `Precision` its average precision on the results. **Note**: We assume that increasing strategy identifiers correspond to increasing execution times and highest precision.

For each epoch `T`, users can specify the `ReceivedRequests` and the `CarbonIntensity` via facts like:

```prolog
reqs(T,ReceivedRequests).
carbon(T,CarbonIntensity).
```

Strategy assignments are denoted via facts of the form

```prolog
assign(T,S).
```

meaning that at time `T` strategy `S` shall be used.

## How to

To try one of the examples in the `examples` folder, simply issue:

```sh
clingo asp_policymaker.lp examples/example<ID>.lp 0
```

For instance, running `example2.pl` will output the following optimal assignment (associated to an estimate of 20915 gCO2-eq carbon emissions):

```sh
$ clingo asp_policymaker.lp examples/example2.lp 0
clingo version 5.5.0
Reading from asp_policymaker.lp ...
Solving...
Answer: 1
assign(1,1) assign(3,1) assign(4,1) assign(5,1) assign(6,1) assign(7,1) assign(8,1) assign(9,1) assign(10,1) assign(11,1) assign(2,2) overallPrecision(90)
Optimization: 25646
Answer: 2
assign(3,0) assign(9,0) assign(1,1) assign(4,1) assign(6,1) assign(7,1) assign(8,1) assign(11,1) assign(2,2) assign(5,2) assign(10,2) overallPrecision(90)
Optimization: 20915
OPTIMUM FOUND

Models       : 2
  Optimum    : yes
Optimization : 20915
Calls        : 1
Time         : 0.218s (Solving: 0.04s 1st Model: 0.01s Unsat: 0.03s)
CPU Time     : 0.206s
```

