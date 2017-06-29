include "globals.mzn";

int: n1;
int: n2;
array[1..n1,1..n1] of 0..1: adjacent1;
array[1..n2,1..n2] of 0..1: adjacent2;

% 0 means unlabelled
array[1..n1] of 0..n1+n2: vLabel1;
array[1..n2] of 0..n1+n2: vLabel2;

% a function from vertices of graph 2 to vertices of graph 1; 0 means not mapped
array[1..n2] of var 0..n1: isomorphism;
var 0..min(n1, n2): size;

constraint size == sum([1 | i in isomorphism where i != 0]); % defining size
constraint alldifferent_except_0(isomorphism); % injectivity
constraint forall(i in 1..n2, j in 1..i-1 % main constraint
    where isomorphism[i] != 0 /\ isomorphism[j] != 0)(
    adjacent2[i,j] == 1 <-> adjacent1[isomorphism[i], isomorphism[j]] == 1);
    
% preserving labels
constraint forall(j in 1..n2)(vLabel2[j] > 0 /\ isomorphism[j] != 0 ->
    vLabel1[isomorphism[j]] == vLabel2[j]);
constraint forall(i in 1..n1, j in 1..n2)(
    vLabel1[i] > 0 /\ isomorphism[j] == i -> vLabel2[j] == vLabel1[i]);

solve maximize size;
output [show(size)];