% assign a strategy to each time slot
1 {assign(T,S) : strategy(S)} 1 :- time(T).

% throw away models where strategies are used inconsistently or precision is too low
:- assign(T1,S1), assign(T2,S2), T1 != T2, S1 < S2, carbon(T1,C1), carbon(T2,C2), C1 > C2.
:- precision(Pr), desiredPrecision(Goal), totReqs(Tot), Pr < Tot * Goal.

% compute precision
precision(Pr) :- Pr = #sum{ RP, T :  RP = R * P, reqs(T,R), strategy(S,_,P), assign(T,S) }.
totReqs(Tot) :- Tot = #sum{ R, T : reqs(T,R) }.

% compute emissions for each time slot TI
emissions(E,TI) :- E = #sum{ CR, T : CR = C * R,  carbon(T,C), reqs(T,R), TI <= T, T <= TF, endtime(TI,D,TF), strategy(S,D,_), assign(TI,S) }, time(TI).

endtime(T,D,TF) :- maxTime(Max), time(T), duration(D), TF = T + D - 1, TF <= Max.
endtime(T,D,Max) :- maxTime(Max), time(T), duration(D), T + D - 1 > Max.

% minimise overall emissions
#minimize { E@2 : emissions(E,T) }.
#maximize { Pr/R@1 : precision(Pr), totReqs(R) }.

#show.
#show overallPrecision(Pr) : precision(P), totReqs(R), Pr = P/R.
#show assign(T,S,C) : time(T), assign(T,S), strategy(S), carbon(T,C).