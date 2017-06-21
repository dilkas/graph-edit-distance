include "globals.mzn";

int: n; % number of vertices
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
var set of 1..n: clique;

constraint forall(i, j in clique where i != j)(adjacent[i,j] == 1);
solve maximize card(clique);

output [show(clique)];
% 5 s on G(40, 0.5)