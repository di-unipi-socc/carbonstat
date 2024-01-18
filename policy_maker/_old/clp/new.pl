:- use_module(library(clpfd)).
:- set_prolog_flag(answer_write_options,[max_depth(0), spacing(next_argument)]).
:- set_prolog_flag(stack_limit, 64 000 000 000).
:- consult('/Users/stefanoforti/Desktop/GitHub/gfcadc/policy_maker/clp/examples/example2.pl').

%%% Main %%%
go(DesiredP, (E,S,P)) :-
    init(Times), minPrecision(DesiredP, MinP, TotReqs), 
    time(findall((E,S,P), solution(MinP, Times, S, E, P), Solutions)),
    sort(Solutions, [(E,S,TmpP)|_]),
    P is TmpP / TotReqs.
    
%%% Constraints %%%
solution(MinP, Times, Strategies, Emissions, Precision) :-
    length(Times, N), length(Strategies, N),  Strategies ins 0..2,          % Domain
    constraints(Strategies, MinP, Precision),                               % Constraints
    label(Strategies),                                                      % Search
    thresholdCoherent(Times, Strategies),
    emissions(Strategies, Emissions).

constraints(Strategies, MinP, Precision) :- 
    Precision #>= MinP, precision(Strategies, Precision).
        
precision(Strategies, Precision) :- 
    precision(Strategies, 1, Precisions), sum(Precisions,#=,Precision).

precision([S|Ss], I, [Pr|Ps]) :- 
    strategy(S, _, P), requestRate(I, R),
    Pr is R * P,
    NewI is I + 1, precision(Ss, NewI, Ps).
precision([], _, []).

thresholdCoherent(Times, Strategies) :-
    \+ (    member(T1,Times), member(T2,Times), dif(T1,T2), 
            nth1(T1, Strategies, S1), nth1(T2, Strategies, S2), S1 < S2, 
            carbonIntensity(T1,C1), carbonIntensity(T2,C2), 
            C1 >= C2    ).


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
init(Times) :- maxTime(M), initLists(M, Ts), reverse(Ts,Times).

initLists(N, [N|Ts]) :- N > 0, N1 is N-1, initLists(N1, Ts).
initLists(0, []).

minPrecision(DesiredP,MinP,TotReqs) :- findall(R, requestRate(_, R), Rs), sumlist(Rs, TotReqs), MinP is TotReqs * DesiredP.