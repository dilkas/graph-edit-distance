include "globals.mzn";

int: n; % number of vertices
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique

constraint forall(i in 1..n, j in 1..i-1)(adjacent[i,j] == 0 -> clique[i] + clique[j] <= 1);
solve maximize sum(clique);

output [show(sum(clique))];