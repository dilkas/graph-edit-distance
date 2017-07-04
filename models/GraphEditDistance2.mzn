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

array[1..n1] of var 0..n2: map; % 0 means deleted
array[1..n2] of var 0..n1: inverseMap; % 0 means inserted
var float: distance;

constraint alldifferent_except_0(map);
constraint alldifferent_except_0(inverseMap);
constraint forall(i in 1..n1 where map[i] != 0)(inverseMap[map[i]] == i);
constraint forall(j in 1..n2 where inverseMap[j] != 0)(map[inverseMap[j]] == j);
constraint distance == sum(i in 1..n1)(if map[i] != 0 then vertexSubstitutionCost[i,map[i]]
        else vertexDeletionCost[i] endif)
    + sum(j in 1..n2)(if inverseMap[j] == 0 then vertexInsertionCost[j] else 0 endif)
    + sum(i in 1..n1, j in 1..i-1 where adjacent1[i,j] == 1)(if map[i] == 0 \/ map[j] == 0 \/
        adjacent2[map[i],map[j]] == 0 then edgeDeletionCost[i,j]
        else edgeSubstitutionCost[i,j,map[i],map[j]] endif)
    + sum(i in 1..n2, j in 1..i-1 where adjacent2[i,j] == 1)(if inverseMap[i] == 0 \/
        inverseMap[j] == 0 \/ adjacent1[inverseMap[i],inverseMap[j]] == 0
        then edgeInsertionCost[i,j] else 0 endif);

solve minimize distance;
%output [show(distance)];