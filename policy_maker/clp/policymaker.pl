:- use_module(library(clpfd)).
:- consult('examples/example2.pl').

%%% Main %%%
go(Solution, DesiredP, Thresholds) :-
    init(Strategies, Times), minPrecision(DesiredP, MinP),
    Strategies ins 0..2, % strategies are numbered from 0 (hp) to 2 (lp)
    time(optimal(Times, MinP, Solution)),
    thresholds(Solution, Thresholds).

optimal(Times, MinP, Solution) :-
    findall((E,P,Strategies), solution(Times, Strategies, E, MinP, P), Solutions), 
    sort(Solutions, [Solution|_]).

solution(Times, Strategies, E, MinP, P) :- 
    assign(Times, Strategies, E, P), % determine a valid sequence of strategies with E emissions and P precision
    constrain(P,MinP).               % constrain the precision P to be at least MinP
  
constrain(P,MinP) :- P #>= MinP.
    
assign(Times, Strategies, E, P) :-
    maplist(selectStrategy, Times, Strategies, Emissions, Precisions), 
    thresholdCoherent(Times, Strategies),
    sum(Precisions, #=, P), sumlist(Emissions, E).

selectStrategy(Time, Strategy, E, P) :-
    strategy(Strategy, Duration, _), requestRate(Time, R), maxTime(MaxTime),
    (Time + Duration =< MaxTime -> EndTime is Time + Duration; EndTime is MaxTime),
    emissions(Time, EndTime, Emissions), E is R * Emissions, 
    precision(R, Strategy, P).

thresholdCoherent(Times, Strategies) :-
    \+ (    
            member(T1,Times), member(T2,Times), dif(T1,T2), 
            nth1(T1, Strategies, S1), nth1(T2, Strategies, S2), S1 < S2, 
            carbonIntensity(T1,C1), carbonIntensity(T2,C2), 
            C1 >= C2
        ).

emissions(StartTime, EndTime, Emissions) :-
    findall(C, (carbonIntensity(I,C), I >= StartTime, I < EndTime), Cs), sumlist(Cs, Emissions).

precision(R, Strategy, Precision) :- strategy(Strategy, _, P), Precision is R * P.

thresholds(Solution, Thresholds) :- 
    Solution = (_,_,Strategies),
    findall((S,T), threshold(T, S, Strategies), Thresholds).
    
threshold(T, S, Strategies) :-
    strategy(S, _, _), 
    findall(C, (carbonIntensity(I,C), nth1(I, Strategies, S)), Cs),
    min_list(Cs, T1), max_list(Cs, T2), T = <->(T1,T2).

%%% Utils %%%
init(Strategies, Times) :- maxTime(M), initLists(M, Strategies, Ts), reverse(Ts,Times).

initLists(N, [_|Ns], [N|Ts]) :- N > 0, N1 is N-1, initLists(N1, Ns, Ts).
initLists(0, [], []).

minPrecision(DesiredP,MinP) :- findall(R, requestRate(_, R), Rs), sumlist(Rs, TotReqs), MinP is TotReqs * DesiredP.
