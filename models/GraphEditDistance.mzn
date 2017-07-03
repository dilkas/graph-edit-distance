include "globals.mzn";

int: n1;
int: n2;
array[1..n1,1..n1] of 0..1: adjacent1;
array[1..n2,1..n2] of 0..1: adjacent2;
array[1..n1] of float: vertexDeletionCost;
array[1..n2] of float: vertexInsertionCost;
array[1..n1,1..n2] of float: vertexSubstitutionCost;
array[1..n1,1..n1] of float: edgeDeletionCost;
array[1..n2,1..n2] of float: edgeInsertionCost;
array[1..n1,1..n1,1..n2,1..n2] of float: edgeSubstitutionCost;

array[1..n1] of var 0..1: vertexDeletion;
array[1..n2] of var 0..1: vertexInsertion;
array[1..n1,1..n2] of var 0..1: vertexSubstitution;
array[1..n1,1..n1] of var 0..1: edgeDeletion;
array[1..n2,1..n2] of var 0..1: edgeInsertion;
array[1..n1,1..n1,1..n2,1..n2] of var 0..1: edgeSubstitution;
var int: distance;

constraint distance == sum(i in 1..n1)(vertexDeletion[i]) + sum(i in 1..n2)(vertexInsertion[i])
    + sum(i in 1..n1, j in 1..n2)(vertexSubstitution[i,j]) + sum(i, j in 1..n1)(edgeDeletion[i,j])
    + sum(i, j in 1..n2)(edgeInsertion[i,j]) + sum(i, j in 1..n1, k, l in 1..n2)(edgeSubstitution[i,j,k,l]);
constraint forall(i in 1..n1)(vertexDeletion[i] == 1 \/
    exists(j in 1..n2)(vertexSubstitution[i,j] == 1));
constraint forall(j in 1..n2)(vertexInsertion[j] == 1 \/
    exists(i in 1..n1)(vertexSubstitution[i,j] == 1));
constraint forall(i, j in 1..n1)(edgeDeletion[i,j] == 1 \/
    exists(k, l in 1..n2)(edgeSubstitution[i,j,k,l] == 1));
constraint forall(k, l in 1..n2)(edgeInsertion[k,l] == 1 \/
    exists(i,j in 1..n1)(edgeSubstitution[i,j,k,l] == 1));
% symmetry
constraint forall(i, j in 1..n1)(edgeDeletion[i,j] == edgeDeletion[j,i]);
constraint forall(i, j in 1..n2)(edgeInsertion[i,j] == edgeInsertion[j,i]);
constraint forall(i, j in 1..n1, k, l in 1..n2)(
    edgeSubstitution[i,j,k,l] == edgeSubstitution[j,i,k,l] /\
    edgeSubstitution[i,j,k,l] == edgeSubstitution[i,j,l,k] /\
    edgeSubstitution[i,j,k,l] == edgeSubstitution[j,i,l,k]);

solve minimize distance;
output [show(distance)];