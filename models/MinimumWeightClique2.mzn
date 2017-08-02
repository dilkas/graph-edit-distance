include "globals.mzn";

int: v1;
int: e1;
int: v2;
int: e2;
int: n = v1+v2+e1+e2+v1*v2+e1*e2; % number of vertices
int: e0 = (v1+1)*(v2+1) - 1; % index of the last vertex operation
array[1..n] of float: weights;
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique
var float: distance;

% clique property
constraint forall(i in 1..n, j in 1..i-1)(
    adjacent[i,j] == 0 -> clique[i]+clique[j] <= 1);
% we must pick a vertex from each independent set
constraint forall(i in 1..v1)(sum(j in 0..v2)(clique[i*(v2+1)+j]) >= 1);
constraint forall(j in 1..v2)(sum(i in 0..v1)(clique[i*(v2+1)+j]) >= 1);
constraint forall(i in 1..e1)(sum(j in 0..e2)(clique[e0+i*(e2+1)+j]) >= 1);
constraint forall(j in 1..e2)(sum(i in 0..e1)(clique[e0+i*(e2+1)+j]) >= 1);
constraint distance == sum(i in 1..n)(clique[i] * weights[i]);

solve minimize distance;