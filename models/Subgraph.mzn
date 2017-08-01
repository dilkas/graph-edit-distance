include "globals.mzn";

% checking if graph 1 is isomorphic to a subgraph of graph 2
int: n1;
int: n2;
array[1..n1,1..n1] of 0..1: adjacent1;
array[1..n2,1..n2] of 0..1: adjacent2;
% a function from vertices of graph 1 to vertices of graph 2
array[1..n1] of var 1..n2: isomorphism;

constraint all_different(isomorphism); % injectivity
constraint forall(i in 1..n1, j in 1..i-1)(
    adjacent1[i,j] == 1 <-> adjacent2[isomorphism[i], isomorphism[j]] == 1);
solve satisfy;
