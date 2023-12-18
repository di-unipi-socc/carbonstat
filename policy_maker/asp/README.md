# ASP Policymaker

This version of the policymaker employs Answer Set Programming. It relies on the [clingo](https://potassco.org/clingo/) grounder and solver.

## Knowledge Representation

Users just need to specify ground domains for the considered time instants, i.e.  ` timeSlot(1..TL).` and a fact `lastTimeSlot(TL)` is needed.

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
adopted(T,S).
```

meaning that strategy `S` shall be used at time `T`.

## How to

To try one of the examples in the `examples` folder, simply issue:

```sh
clingo asp_policymaker.pl examples/example<ID>.pl 0
```

For instance, running `example2.pl` will output the following optimal assignment (associated to an estimate of 20915 gCO2-eq carbon emissions):

```sh
$ clingo asp_policymaker.pl examples/example2.pl 0
clingo version 5.5.0
Reading from versions/e.pl ...
Solving...
Answer: 1
policyAttimeSlot(9,0) policyAttimeSlot(1,1) policyAttimeSlot(2,1) policyAttimeSlot(3,1) policyAttimeSlot(4,1) policyAttimeSlot(5,1) policyAttimeSlot(6,1) policyAttimeSlot(7,1) policyAttimeSlot(8,1) policyAttimeSlot(10,1) policyAttimeSlot(11,1) achievedPrecision(88)
Optimization: 23298 88
Answer: 2
policyAttimeSlot(3,0) policyAttimeSlot(9,0) policyAttimeSlot(11,0) policyAttimeSlot(1,1) policyAttimeSlot(4,1) policyAttimeSlot(6,1) policyAttimeSlot(7,1) policyAttimeSlot(8,1) policyAttimeSlot(2,2) policyAttimeSlot(5,2) policyAttimeSlot(10,2) achievedPrecision(88)
Optimization: 23165 88
Answer: 3
policyAttimeSlot(3,0) policyAttimeSlot(7,0) policyAttimeSlot(9,0) policyAttimeSlot(11,0) policyAttimeSlot(1,1) policyAttimeSlot(6,1) policyAttimeSlot(2,2) policyAttimeSlot(4,2) policyAttimeSlot(5,2) policyAttimeSlot(8,2) policyAttimeSlot(10,2) achievedPrecision(88)
Optimization: 20996 88
OPTIMUM FOUND

Models       : 3
  Optimum    : yes
Optimization : 20996 88
Calls        : 1
Time         : 0.121s (Solving: 0.01s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.121s
```

