% Randomly choose adopted strategy for each time slot
1 {adopted(T,S) : strategy(S,_,_)} 1 :- timeSlot(T).

% Discard models with incoherent strategies or insufficient precision
:- adopted(T1,S1), adopted(T2,S2), carbon(T1,C1), carbon(T2,C2), T1 != T2, S1 < S2, C1 > C2. 
:- adopted(T1,S1), adopted(T2,S2), carbon(T1,C), carbon(T2,C), T1 != T2, S1 != S2.   

:- desiredPrecision(DP), sumOfPrecisions(Ps), totalReqs(Rs), Ps < Rs * DP.
% with
sumOfPrecisions(Ps) :- Ps = #sum{ RP, T : reqs(T,R), adopted(T,S), strategy(S,_,P), RP = R * P }.
totalReqs(Rs)       :- Rs = #sum{ R , T : reqs(T,R) }.

% compute emissions for each time slot
emissions(E,TI) :-  E = #sum{ CR, T : TI <= T, T <= TI + D - 1, T <= TL, carbon(T,C), CR = C * RI}, reqs(TI,RI), adopted(TI,S), timeSlot(TI), strategy(S,D,_),lastTimeSlot(TL).

#minimize { E@2,TI : emissions(E,TI) }.
#minimize { P/R@1 : sumOfPrecisions(P), totalReqs(R) }.

#show.
#show achievedPrecision(Pr) : sumOfPrecisions(P), totalReqs(R), Pr = P/R.
#show policyAttimeSlot(T,S) : timeSlot(T), adopted(T,S).


% tf(TI,S,TI+D-1) :- lastTimeSlot(TL), timeSlot(TI), timeSlot(TI+D-1), strategy(S,D,_).
% tf(TL,S,TL) :- lastTimeSlot(TL), timeSlot(TL), strategy(S,_,_).