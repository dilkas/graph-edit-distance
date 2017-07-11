include "globals.mzn";

int: v1;
int: v2;
int: n = (v1+1)*(v2+1)-1; % number of vertices
array[1..n] of float: vertexWeights;
array[1..n,1..n] of float: edgeWeights;
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique
var float: distance;

% clique property
constraint forall(i in 1..n, j in 1..i-1)(
    adjacent[i,j] == 0 -> clique[i] + clique[j] <= 1);
% we must pick a vertex from each independent set
constraint forall(i in 1..v1)(exists(j in 0..v2)(clique[i*(v2+1)+j] == 1));
constraint forall(j in 1..v2)(exists(i in 0..v1)(clique[i*(v2+1)+j] == 1));
constraint distance ==
    sum(i in 1..n)(if clique[i] == 1 then vertexWeights[i] else 0 endif)
    + sum(i in 1..n, j in 1..i-1)(
        if clique[i] == 1 /\ clique[j] == 1 then edgeWeights[i,j] else 0 endif);

solve maximize distance;