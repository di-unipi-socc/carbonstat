#minimize { TotE/TotR@1 : sumOfErrors(TotE), totalReqs(TotR) }.                                 % Eq. (1)
sumOfErrors(TotE) :- TotE = #sum{ ER, I : assignment(I,J), timeslot(I,_,Ri), strategy(J,_,Ej), ER = Ri * Ej }.
totalReqs(TotR) :- TotR = #sum{ Ri :  timeslot(I,_,Ri)}.

#minimize { TotC@2 : emissions(TotC) }.                                                         % Eq. (2)
emissions(TotC) :- TotC = Ci * Ri * Dj, assignment(I,J), timeslot(I,Ci,Ri), strategy(J,Dj,_). 

:- maxError(Epsilon), sumOfErrors(TotE), totalReqs(TotR), TotE > Epsilon * TotR.                % Eq. (3)

1 {assignment(I,J) : strategy(J,_,_)} 1 :- timeslot(I,_,_).                                     % Eq. (4)

#show.
#show assignment/2.

maxError(6).

strategy(1, 1, 15).
strategy(2, 2, 5).
strategy(3, 3, 0).

timeslot(1, 94, 39).
timeslot(2, 21, 78).
timeslot(3, 15, 96).
timeslot(4, 20, 64).
timeslot(5, 83, 56).
timeslot(6, 77, 68).
timeslot(7, 82, 82).
timeslot(8, 70, 19).
timeslot(9, 20, 48).
timeslot(10, 20, 20).