include "globals.mzn";

int: n; % number of vertices
array[1..n,1..n] of 0..1: adjacent; % adjacency matrix
array[1..n] of var 0..1: clique; % whether a vertex is part of the clique

constraint forall(i, j in 1..n where i != j)(clique[i] == 1 /\ clique[j] == 1 -> adjacent[i,j] == 1);
solve maximize sum(clique);

output [show(sum(clique))];
% 5 min 11 s on brock200_4 with gecode
% chuffed is slower
% 45 ms on G(40, 0.5)

% n = 70
% p   t           #clique
% 0.1 52 ms       4
% 0.2 52 ms       5
% 0.3 57 ms       5
% 0.4 69 ms       7
% 0.5 88 ms       8
% 0.6 149 ms      10
% 0.7 535 ms      13
% 0.8 3 s 151 ms  17
% 0.9 46 s 360 ms 25

% n = 55
% p       t
% 0.90 3 s 240 ms
% 0.91 5 s 344 ms
% 0.92 11 s 714 ms
% 0.93 19 s 12 ms
% 0.94 15 s 185 ms
% 0.95 22 s 71 ms
% 0.96 33 s 451 ms
% 0.97 25 s 753 ms
% 0.98 3 s 403 ms
% 0.99 93 ms