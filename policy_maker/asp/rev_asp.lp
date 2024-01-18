% Randomly choose adopted strategy for each time slot
1 {adopted(S,C,R) : strategy(S,_,_)} 1 :- data(C,R).

% Discard models with incoherent strategies or insufficient precision
:- adopted(S1,C1,R1), adopted(S2,C2,R2), S1 < S2, C1 <= C2, R1 <= R2.

:- maxError(DP), sumOfErrors(Ps), totalReqs(Rs), Ps > Rs * DP.
% with
sumOfErrors(Ps) :- Ps = #sum{ RP : data(C,R), adopted(S,C,R), strategy(S,_,P), RP = R * P }.
totalReqs(Rs) :- Rs = #sum{ R : data(T,_,R) }.

% compute emissions for a time slot
% C = [mgCO2/kWs] * [#reqs] * [s]
emissions(E) :- E = C * R * D, data(C,R), adopted(S,C,R), strategy(S,D,_).

#minimize { E@2 : emissions(E) }.
#minimize { P/R@1 : sumOfErrors(P), totalReqs(R) }.

#show.
#show adopted/3.
#show thresholds(S,MaxR,MaxC) : 
    strategy(S,_,_), 
        MaxR = #max{ R : adopted(S,C,R)  },
        MaxC = #max{ C : adopted(S,C,R)  }.

%%%%
maxError(6).

strategy(0, 1, 15).
strategy(1, 2, 5).
strategy(2, 3, 0).

data(94, 390).
data(212, 789).
data(157, 968).
data(206, 646).
data(83, 569).
data(77, 680).
data(82, 822).
data(70, 198).
data(207, 489).
data(204, 206).
%%%%