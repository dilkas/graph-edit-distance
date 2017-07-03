CONTENTS OF THIS FILE
---------------------
   
 * Reference
 * Authors
 * Database Content

Reference
---------------------
A Graph Database Repository and Performance Evaluation Metrics for Graph Edit Distance, submitted to GBR2015.


Authors
---------------------
Zeina Abu-Aisheh, 3rd year PhD student at François Rabelais University, Tours, France.
Romain Raveaux, Assistant Professor at François Rabelais University, Tours, France.
Jean-Yves Ramel, Professor at François Rabelais University, Tours, France.  


Database Content
---------------------
 - GREC-cost-function

   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. For all the subsets of GREC,  tau_{node}, tau_{edge} and alpha are set to 90, 15 and 
   0.5 respectively. The cost function is written in Java and is found in the GREC-GED folder.
 
 - GREC-low-level-info
   
  The pairwise comparisons of each of the aforementioned subsets is performed. For each comparison, the following information is added:
  1- The name of each pair of graphs d(g_1,g_2).
  2- The number of vertices of each pair of graphs.
  3- The number of edges of each pair of graphs.
  4- The name of a graph edit distance (GED) method P that succeeds at finding the best distance for d(g_1,g_2).
  5- A parameter used for the method BeamSearch GED which represents the size of the stack (1, 10 or 100 in the experiments).
  6- The best distance that was found by method P.
  7- A boolean value that tells whether the found solution is optimal or not.
  8- The classes of graphs g_1 and g_2.
  9- The matching sequence found by method P.
  10- For instance Node:3->4=0.0 means that substituting vertex 3 on graph g_1 with vertex 4 on graph g_2 costs 0.0. Moreover, Edge:1_<>2->1_<>5=4.0 means that substituting
      1_<>2 on graph g_1 with edge 1_<>5 on graph g_2 costs 4.0. On the other hand, Node:3->eps=4.0 means that deleting vertex 3 costs 4.0 while vertex:eps->4=6.0 means that
      inserting vertex 4 costs 6.0.	 
 
 - GREC-subsets
   Contains 4 subsets (GREC-5, GREC-10, GREC-15, GREC-20 and GREC-MIX) from the GREC database, each of which has 10 graphs. 100 pairwise matchings were conducted per subset.
   GREC-MIX represents 10 graphs that were picked up from GREC-5, GREC-10, GREC-15 and GREC-20 and were put in this mixed database.

 - Information about GREC

   In GREC, 22 symbols from architecture and electronics are represented in this data set. Those symbols consist of lines, arcs and circles. Each symbol class has a prototype image
   occurs at ve levels of distortions. Distortions happen by dividing the primitive lines of the symbols into sub-parts where the shifting within a specied distance is applied to 
   the ending points of the lines sub-parts. Those distorted images are transformed into attributed graphs where nodes represents the relative length of line's 
   sub-part (i.e. ration of actual line length to the length of the longest line in the symbol .). Edges represent connection points and are attributed with the angle between two lines. 
   This data set consists of 1,100 graphs where graphs are uniformly distributed between 22 symbols. The resulting data set is split into a training and a validation set of size 286 each, 
   and a test set of size size 528. The classication rate achieved on this data set is 95.5%.
 