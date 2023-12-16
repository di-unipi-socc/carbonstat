
time(1..11).
strategy(0..2).
duration(1..100).

maxTime(11).
desiredPrecision(88).

strategy(0, 1, 80).
strategy(1, 2, 90).
strategy(2, 3, 100).

reqs(1, 3).
reqs(2, 4).
reqs(3, 5).
reqs(4, 2).
reqs(5, 1).
reqs(6, 6).
reqs(7, 7).
reqs(8, 2).
reqs(9, 5).
reqs(10, 6).
reqs(11, 7). 

carbon(1, 100).
carbon(2, 1000).
carbon(3, 5).
carbon(4, 200).
carbon(5, 1000).
carbon(6, 100).
carbon(7, 67).
carbon(8, 567).
carbon(9, 2).
carbon(10, 800).
carbon(11, 5).


% assign a strategy to each time slot
1 {assign(T,S) : strategy(S)} 1 :- time(T), reqs(T,R).

% throw away models where strategies are used inconsistently or precision is too low
:- assign(T1,S1), assign(T2,S2), S1 < S2, carbon(T1,C1), carbon(T2,C2), C1 > C2.
:- precision(Pr), desiredPrecision(Goal), totReqs(Tot), Pr < Tot * Goal.

% compute cost and precision
precision(Pr) :- Pr = #sum{ RP, T :  RP = R * P, reqs(T,R), strategy(S,_,P), assign(T,S) }.
totReqs(Tot) :- Tot = #sum{ R, T : reqs(T,R) }.

emissions(E,TI) :- E = #sum{ CR, T : CR = C * R,  carbon(T,C), reqs(T,R), TI <= T, T <= TF, finalTime(TI,D,TF), strategy(S,D,_), assign(TI,S) }, time(TI).
totEmissions(TotE) :- TotE = #sum{ E, T : emissions(E,T) }, time(T).

finalTime(T,D,TF) :- maxTime(Max), time(T), duration(D), T + D - 1 <= Max, TF = T + D - 1, time(TF).
finalTime(T,D,Max) :- maxTime(Max), time(T), duration(D), T + D - 1 > Max.

#minimize { E : totEmissions(E) }.

#show.
#show overallPrecision(Pr) : precision(P), totReqs(R), Pr = P/R.
#show totEmissions(E) : totEmissions(E).
#show assign(T,S) : time(T), assign(T,S), strategy(S).

