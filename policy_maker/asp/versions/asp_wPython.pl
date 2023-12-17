1 {assign(T,S) : strategy(S)} 1 :- time(T).

:- assign(T1,S1), assign(T2,S2), T1 != T2, S1 < S2, carbon(T1,C1), carbon(T2,C2), C1 > C2. % TODO: reqs(T1,R1), reqs(T2,R2), R1*C1 > R2*C2.
:- precision(Pr), desiredPrecision(Goal), totReqs(Tot), Pr < Tot * Goal.

precision(Pr) :- Pr = #sum{ RP, T :  RP = R * P, reqs(T,R), strategy(S,_,P), assign(T,S) }.
totReqs(Tot) :- Tot = #sum{ R, T : reqs(T,R) }.

emissions(E,TI) :- E = #sum{ CR, T : CR = C * R,  carbon(T,C), reqs(T,R), TI <= T, T <= TF, finalTime(TI,S,TF), assign(TI,S) }, time(TI).

finalTime(T,S,@final_time(T,D,Max)) :- strategy(S,D,_), time(T), duration(D), maxTime(Max).

#minimize { E : emissions(E,T) }.

#show.
#show overallPrecision(Pr) : precision(P), totReqs(R), Pr = P/R.
#show assign(T,S,C) : time(T), assign(T,S), strategy(S), carbon(T,C).

#script(python)
import clingo

def final_time(ti, d, max):
    tf = ti.number + d.number - 1 if ti.number + d.number - 1 <= max.number else max.number
    return clingo.Number(tf)
#end.