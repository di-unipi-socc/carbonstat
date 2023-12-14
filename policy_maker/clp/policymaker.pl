:- use_module(library(clpfd)).
:- consult('examples/example2.pl').

%%% Main %%%
go(DesiredP, Best) :-
    init(Strategies, Times), minPrecision(DesiredP, MinP),
    Strategies ins 0..2, % strategies are numbered from 0 (hp) to 2 (lp)
    P #>= MinP, % precision is at least MinP
    time(findall((E,P,S), solution(Times, S, E, P), Sols)),
    sort(Sols, [Best|_]), write(Best), nl.

solution(Times, Strategies, Emissions, Precision) :-
    maplist(selectStrategy, Times, Strategies, Precisions), 
    thresholdCoherent(Times, Strategies),
    sum(Precisions,#=,Precision),
    emissions(Strategies, Emissions).

selectStrategy(Time, Strategy, P) :-
    strategy(Strategy, _, _), requestRate(Time, R), precision(R, Strategy, P).

thresholdCoherent(Times, Strategies) :-
    \+ (    
            member(T1,Times), member(T2,Times), dif(T1,T2), 
            nth1(T1, Strategies, S1), nth1(T2, Strategies, S2), S1 < S2, 
            carbonIntensity(T1,C1), carbonIntensity(T2,C2), 
            C1 >= C2
        ).

precision(R, Strategy, Precision) :- strategy(Strategy, _, P), Precision is R * P.

emissions(Solution, TotalEmissions) :-
    emissions(Solution, 1, Emissions), sumlist(Emissions, TotalEmissions).

emissions([S|Ss], I, [E|Es]) :-
    strategy(S, Duration, _), requestRate(I, R), maxTime(MaxTime),
    (I + Duration =< MaxTime -> EndTime is I + Duration; EndTime is MaxTime),
    emitted(I, EndTime, Emissions), E is R * Emissions,
    NewI is I + 1, emissions(Ss, NewI, Es).
emissions([], _, []).

emitted(StartTime, EndTime, Emissions) :-
    findall(C, (carbonIntensity(I,C), I >= StartTime, I < EndTime), Cs), sumlist(Cs, Emissions).

%%% Utils %%%
init(Strategies, Times) :- maxTime(M), initLists(M, Strategies, Ts), reverse(Ts,Times).

initLists(N, [_|Ns], [N|Ts]) :- N > 0, N1 is N-1, initLists(N1, Ns, Ts).
initLists(0, [], []).

minPrecision(DesiredP,MinP) :- findall(R, requestRate(_, R), Rs), sumlist(Rs, TotReqs), MinP is TotReqs * DesiredP.
