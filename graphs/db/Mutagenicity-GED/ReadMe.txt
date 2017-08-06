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
 - MUTA-cost-function

   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. For all the subsets of MUTA, tau_{node}, tau_{edge} and alpha are set to 11, 1 and 0.75 respectively.
   The cost function is written in Java and is found in the MUTA-GED folder.
 
 - MUTA-low-level-info
   
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
 
 - MUTA-subsets

   Contains 4 subsets (MUTA-10, MUTA-20, MUTA-30, MUTA-40, MUTA-50, MUTA-60, MUTA-70 and MUTA-MIX) from the MUTA database, each of which has 10 graphs. 100 pairwise matchings were conducted per subset.
   MUTA-MIX represents 10 graphs that were picked up from MUTA-10, MUTA-20, MUTA-30, MUTA-40, MUTA-50, MUTA-60 and MUTA-70 and were put in this mixed database.

 - Information about MUTA

   Mutagenicity (or MUTA) is the capacity of a chemical or physical agent to cause permanent genetic alterations.
   MUTA simply transformed into attributed graphs where nodes represent atoms and are labeled with the number of the corresponding  chemical symbol whereas edges
   represent the covalent bonds and are labeled with the valence (i.e. the combining power of atoms) of the linkage. 4,337 elements are represented in this dataset 
   (2,401 mutagen elements and 1,936 non-mutagen elements) which are divided into: a training set of size 1,500, a validation set of size 500, and a test set of 
   size 2,337. The classication rate achieved on this data set is 71.5%.
 