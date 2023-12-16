% assign a strategy to each time slot
1 {assign(T,S) : strategy(S)} 1 :- time(T), reqs(T,R).

% throw away models where strategies are used inconsistently or precision is too low
:- assign(T1,S1), assign(T2,S2), S1 < S2, carbon(T1,C1), carbon(T2,C2), C1 > C2.
:- precision(Pr), desiredPrecision(Goal), totReqs(Tot), Pr < Tot * Goal.

% compute cost and precision
precision(Pr) :- Pr = #sum{ RP, T :  RP = R * P, reqs(T,R), strategy(S,_,P), assign(T,S) }.
totReqs(Tot) :- Tot = #sum{ R, T : reqs(T,R) }.

emissions(E,TI) :- E = #sum{ CR, T : CR = C * R,  carbon(T,C), reqs(T,R), TI <= T, T <= TF, finalTime(TI,D,TF), strategy(S,D,_), assign(TI,S) }, time(TI).

finalTime(T,D,TF) :- maxTime(Max), time(T), duration(D), T + D - 1 <= Max, TF = T + D - 1, time(TF).
finalTime(T,D,Max) :- maxTime(Max), time(T), duration(D), T + D - 1 > Max.

#minimize { E : emissions(E,T) }.

#show.
#show overallPrecision(Pr) : precision(P), totReqs(R), Pr = P/R.
#show assign(T,S,C) : time(T), assign(T,S), strategy(S), carbon(T,C).