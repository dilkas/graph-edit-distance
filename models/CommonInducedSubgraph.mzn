include "globals.mzn";

int: n1;
int: n2;
array[1..n1,1..n1] of 0..1: adjacent1;
array[1..n2,1..n2] of 0..1: adjacent2;
% a function from vertices of graph 2 to vertices of graph 1; 0 means not mapped
array[1..n2] of var 0..n1: isomorphism;

constraint alldifferent_except_0(isomorphism);
constraint forall(i in 1..n2, j in 1..i-1 where isomorphism[i] != 0 /\ isomorphism[j] != 0)(
    adjacent2[i,j] == 1 <-> adjacent1[isomorphism[i], isomorphism[j]] == 1);
solve maximize sum([1 | i in isomorphism where i != 0]);