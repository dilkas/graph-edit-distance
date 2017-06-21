include "globals.mzn";

int: n; % number of vertices
int: k; % size of the clique we're looking for
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique

constraint forall(i, j in 1..n where i != j)(clique[i] == 1 /\ clique[j] == 1 -> adjacent[i,j] == 1);
constraint sum(clique) == k;
solve satisfy;