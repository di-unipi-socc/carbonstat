% timestamp(I, Ci, Ri)
%  Ci is measured in mgCO2-eq/W*ms
%  Ri is measured in hundred's of requests per half hour

#minimize { TotE/TotR@1 : sumOfErrors(TotE), totalReqs(TotR) }.                                 % Eq. (1)
sumOfErrors(TotE) :- TotE = #sum{ ER, I : assignment(I,J), timeslot(I,_,Ri), strategy(J,_,Ej), ER = Ri * Ej }.
totalReqs(TotR) :- TotR = #sum{ Ri :  timeslot(I,_,Ri)}.

#minimize { TotC@2 : emissions(TotC) }.                                                         % Eq. (2)
emissions(TotC) :- TotC = Ci * Ri * Dj, assignment(I,J), timeslot(I,Ci,Ri), strategy(J,Dj,_). 

:- maxError(Epsilon), sumOfErrors(TotE), totalReqs(TotR), TotE > Epsilon * TotR.                % Eq. (3)

:- timeslot(I1,C1,R1), timeslot(I2,C2,R2), C2 > C1, R2 > R1, assignment(I1,J1), assignment(I2,J2), strategy(J1,D1,_), strategy(J2,D2,_), D2 > D1.                                             % Eq. (4)

1 {assignment(I,J) : strategy(J,_,_)} 1 :- timeslot(I,_,_).                                     % Eq. (5)

:- timeslot(I1,C1,R1), timeslot(I2,C2,R2), C2 > C1, R2 > R1, 
    assignment(I1,J1), assignment(I2,J2), 
    strategy(J1,D1,_), strategy(J2,D2,_), D2 > D1.

#show.
#show assignment/2.


