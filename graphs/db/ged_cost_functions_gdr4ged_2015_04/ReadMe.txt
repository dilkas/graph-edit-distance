CONTENTS OF THIS FILE
---------------------
   
 * Reference
 * Authors
 * Content

Reference
---------------------
A Graph Database Repository and Performance Evaluation Metrics for Graph Edit Distance, submitted to GBR2015.
http://www.rfai.li.univ-tours.fr/PublicData/GDR4GED/home.html


Authors
---------------------
Zeina Abu-Aisheh, 3rd year PhD student at François Rabelais University, Tours, France.
Romain Raveaux, Assistant Professor at François Rabelais University, Tours, France.
Jean-Yves Ramel, Professor at François Rabelais University, Tours, France.  


Content
---------------------
- MUTA-cost-function
   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. For all the subsets of MUTA, tau_{node}, tau_{edge} and alpha are set to 11, 1 and 0.75 respectively.
   The cost function is written in Java and is found in the MUTA-GED folder.
   The cost function has written in Java by kaspar Reisen [1,2]

- Protein-cost-function
   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. For all the subsets of Protein,  tau_{vertex}, tau_{edge} and alpha are set to
   11, 1 and 0.75 respectively. The cost function is written in Java and is found in the Protein-GED folder.
   The cost function has written in Java by kaspar Reisen [1,2] 

- GREC-cost-function
   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. For all the subsets of GREC,  tau_{node}, tau_{edge} and alpha are set to 90, 15 and 
   0.5 respectively. The cost function is written in Java and is found in the GREC-GED folder.
   The cost function has written in Java by kaspar Reisen [1,2] 

- CMU-cost-function
   Two meta parameters are included tau_{vertex} and tau_{edge} where tau_{vertex} denotes a vertex deletion or insertion whereas tau_{edge}
   denotes an edge deletion or insertion. Both tau_{vertex} and tau_{edge} are non-negative parameters. A third meta parameter alpha is integrated to control whether
   the edit operation cost on the vertices or on the edges is more important. tau_{node}, tau_{edge} and alpha are set to 100000, 100000 and 0.5 respectively.



References
-----------
[1] K. Riesen, PhD manuscript, Graph Classification and Clustering Based on Vector Space Embedding, Univiersity of Bern. 2010

[2] Kaspar Riesen, Horst Bunke, Iam graph database repository for graph based pattern recognition and machine learning (2008) 287-297.
 
   