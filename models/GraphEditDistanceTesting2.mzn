include "globals.mzn";

int: n1;
int: n2;
array[1..n1,1..n1] of 0..1: adjacent1;
array[1..n2,1..n2] of 0..1: adjacent2;
array[1..n2] of int: vertexInsertionCost;
array[1..n1,0..n2] of int: vertexSubstitutionCost;
array[1..n1,1..n1] of int: edgeDeletionCost;
array[1..n2,1..n2] of int: edgeInsertionCost;
array[1..n1,1..n1,1..n2,1..n2] of int: edgeSubstitutionCost;

array[1..n1] of var 0..n2: map; % 0 means deleted
array[1..n2] of var 0..n1: inverseMap; % 0 means inserted
var int: vertexDistance;
var int: edgeDistance;
var int: distance;

constraint alldifferent_except_0(map);
constraint alldifferent_except_0(inverseMap);
constraint forall(i in 1..n1 where map[i] != 0)(inverseMap[map[i]] == i);
constraint forall(j in 1..n2 where inverseMap[j] != 0)(map[inverseMap[j]] == j);
constraint vertexDistance == sum(i in 1..n1)(vertexSubstitutionCost[i,map[i]])
    + sum(j in 1..n2)(if inverseMap[j] == 0 then vertexInsertionCost[j] else 0 endif);
constraint edgeDistance == sum(i in 1..n1, j in 1..i-1 where adjacent1[i,j] == 1)(
        if map[i] == 0 \/ map[j] == 0 \/ adjacent2[map[i],map[j]] == 0
        then edgeDeletionCost[i,j]
        else edgeSubstitutionCost[i,j,map[i],map[j]] endif)
    + sum(i in 1..n2, j in 1..i-1 where adjacent2[i,j] == 1)(if inverseMap[i] == 0 \/
        inverseMap[j] == 0 \/ adjacent1[inverseMap[i],inverseMap[j]] == 0
        then edgeInsertionCost[i,j] else 0 endif);
constraint distance == vertexDistance + edgeDistance;

%solve minimize vertexDistance;
solve minimize distance;