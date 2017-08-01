include "globals.mzn";

int: n; % number of vertices
int: k; % size of the clique we're looking for
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
% a vertex i can be part of a clique of size k only if deg(i) >= k - 1
set of 1..n: possible = {i | i in 1..n where sum(j in 1..n)(
    adjacent[i,j]) >= k - 1};
array[possible] of var 0..1: clique; % whether a vertex is part of the clique

constraint sum(clique) == k;
constraint forall(i, j in possible where i < j)(
    adjacent[i,j] == 0 -> clique[i] + clique[j] <= 1);
solve :: int_search(clique, input_order, indomain_max, complete)
    satisfy;
    
output [show(sum(clique))];