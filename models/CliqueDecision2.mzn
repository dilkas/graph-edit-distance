include "globals.mzn";

int: n; % number of vertices
int: k; % size of the clique we're looking for
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique

constraint sum(clique) == k;
constraint forall(i in 1..n, j in 1..i-1 where adjacent[i,j] == 0)(
    clique[i] + clique[j] <= 1);
solve :: int_search(clique, input_order, indomain_max, complete)
    satisfy;
    
output [show(sum(clique))];