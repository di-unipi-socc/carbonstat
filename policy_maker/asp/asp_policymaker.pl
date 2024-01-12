% Randomly choose adopted strategy for each time slot
1 {adopted(T,S) : strategy(S,_,_)} 1 :- timeSlot(T).

% Discard models with incoherent strategies or insufficient precision
:- adopted(T1,S1), adopted(T2,S2), T1 != T2, S1 < S2, carbon(T1,C1), carbon(T2,C2), C1 <= C2, reqs(T1,R1), reqs(T2,R2), R1 <= R2.

:- desiredPrecision(DP), sumOfPrecisions(Ps), totalReqs(Rs), Ps < Rs * DP.
% with
sumOfPrecisions(Ps) :- Ps = #sum{ RP, T : reqs(T,R), adopted(T,S), strategy(S,_,P), RP = R * P }.
totalReqs(Rs)       :- Rs = #sum{ R , T : reqs(T,R) }.

% compute emissions for a time slot
emissions(E) :-  E = C*R*D, timeSlot(T), carbon(T,C), reqs(T,R), adopted(T,S), strategy(S,D,_).

#minimize { E@2 : emissions(E) }.
#maximize { P/R@1 : sumOfPrecisions(P), totalReqs(R) }.

#show.
% #show achievedPrecision(Pr) : sumOfPrecisions(P), totalReqs(R), Pr = P/R.
% #show policyAttimeSlot(T,S) : timeSlot(T), adopted(T,S).
#show scr(T,S,C,R) : timeSlot(T), carbon(T,C), reqs(T,R), adopted(T,S).
#show thresholds(S,MaxR,MaxC) : 
    strategy(S,_,_), 
        MaxR = #max{ R, T : reqs(T,R),  adopted(T,S), timeSlot(T)},
        MaxC = #max{ C, T : carbon(T,C), adopted(T,S), timeSlot(T) }.
