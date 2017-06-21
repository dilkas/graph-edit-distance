include "globals.mzn";

int: n; % number of vertices
int: k; % number of colors
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 1..k: colors; % each vertex is assigned a color

constraint forall(i in 1..n, j in 1..i-1 where adjacent[i,j] == 1)(colors[i] != colors[j]);
solve satisfy;