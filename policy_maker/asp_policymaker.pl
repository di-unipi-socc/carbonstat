% timestamp(I, Ci, Ri)
%  Ci is measured in mgCO2-eq/W*ms
%  Ri is measured in hundred's of requests per half hour

#minimize { TotE/TotR@1 : sumOfErrors(TotE), totalReqs(TotR) }.                                 % Eq. (1)
sumOfErrors(TotE) :- TotE = #sum{ ER, I : assignment(I,J), timeslot(I,_,Ri), strategy(J,_,Ej), ER = Ri * Ej }.
totalReqs(TotR) :- TotR = #sum{ Ri :  timeslot(I,_,Ri)}.

#minimize { TotC@2 : emissions(TotC) }.                                                         % Eq. (2)
emissions(TotC) :- TotC = Ci * Ri * Dj, assignment(I,J), timeslot(I,Ci,Ri), strategy(J,Dj,_). 

:- maxError(Epsilon), sumOfErrors(TotE), totalReqs(TotR), TotE > Epsilon * TotR.                % Eq. (3)

1 {assignment(I,J) : strategy(J,_,_)} 1 :- timeslot(I,_,_).                                     % Eq. (4)

#show.
#show assignment/2.

% strategy(id, exectime, error)
%  exectime in ms
%  error in percentage
maxError(8).

strategy(1, 1, 15).
strategy(2, 2, 5).
strategy(3, 3, 0).

timeslot(1, 21, 1).
timeslot(2, 20, 2).
timeslot(3, 18, 2).
timeslot(4, 20, 3).
timeslot(5, 21, 3).
timeslot(6, 20, 3).
timeslot(7, 18, 4).
timeslot(8, 19, 5).
timeslot(9, 19, 5).
timeslot(10, 19, 5).
timeslot(11, 18, 6).
timeslot(12, 20, 7).
timeslot(13, 21, 7).
timeslot(14, 21, 8).
timeslot(15, 21, 8).
timeslot(16, 22, 10).
timeslot(17, 20, 10).
timeslot(18, 21, 10).
timeslot(19, 21, 9).
timeslot(20, 19, 9).
timeslot(21, 23, 8).
timeslot(22, 22, 7).
timeslot(23, 21, 6).
timeslot(24, 25, 6).
timeslot(25, 23, 5).
timeslot(26, 25, 6).
timeslot(27, 25, 6).
timeslot(28, 24, 7).
timeslot(29, 25, 8).
timeslot(30, 26, 8).
timeslot(31, 27, 9).
timeslot(32, 30, 10).
timeslot(33, 34, 11).
timeslot(34, 38, 10).
timeslot(35, 48, 9).
timeslot(36, 44, 7).
timeslot(37, 44, 6).
timeslot(38, 44, 6).
timeslot(39, 45, 5).
timeslot(40, 44, 4).
timeslot(41, 41, 3).
timeslot(42, 44, 3).
timeslot(43, 45, 3).
timeslot(44, 47, 2).
timeslot(45, 50, 2).
timeslot(46, 52, 2).
timeslot(47, 43, 1).
timeslot(48, 42, 1).

