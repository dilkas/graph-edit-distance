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
constraint forall(i in 1..v1)(sum(j in 0..v2)(clique[i*(v2+1)+j]) >= 1);
constraint forall(j in 1..v2)(sum(i in 0..v1)(clique[i*(v2+1)+j]) >= 1);
constraint distance == sum(i in 1..n)(clique[i] * vertexWeights[i])
    + sum(i in 1..n, j in 1..i-1)(clique[i] * clique[j] * edgeWeights[i,j]);

solve minimize distance;
output [show(distance)];