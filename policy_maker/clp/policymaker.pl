:- use_module(library(clpfd)).
:- set_prolog_flag(answer_write_options,[max_depth(0)]).
:- consult('examples/example2.pl').

%%% Main %%%
go(DesiredP, (EF,PF,S)) :-
    init(S, Times), minPrecision(DesiredP, MinP,TotReqs),
    time(findall((E,P,S), solution(MinP,Times,S,E,P), Sols)),
    sort(Sols, [(EF,PI,S)|_]), PF is PI / TotReqs. % sort solutions by increasing emissions, take first

solution(MinP, Times, Strategies, Emissions, Precision) :-
    Strategies ins 0..2, % strategies are numbered from 0 (hp) to 2 (lp)
    Precision #>= MinP,          % precision is at least MinP
    maplist(selectStrategy, Times, Strategies, Precisions), 
    thresholdCoherent(Times, Strategies),
    sum(Precisions,#=,Precision),
    emissions(Strategies, Emissions).

selectStrategy(Time, Strategy, P) :- requestRate(Time, R), precision(R, Strategy, P).

thresholdCoherent(Times, Strategies) :-
    \+ (    member(T1,Times), member(T2,Times), dif(T1,T2), 
            nth1(T1, Strategies, S1), nth1(T2, Strategies, S2), S1 < S2, 
            carbonIntensity(T1,C1), carbonIntensity(T2,C2), 
            C1 >= C2    ).

precision(R, Strategy, Precision) :- strategy(Strategy, _, P), Precision is R * P.

emissions(Solution, Emissions) :- emissions(Solution, 1, Es), sumlist(Es, Emissions).

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

minPrecision(DesiredP,MinP,TotReqs) :- findall(R, requestRate(_, R), Rs), sumlist(Rs, TotReqs), MinP is TotReqs * DesiredP.