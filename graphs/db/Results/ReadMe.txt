CONTENTS OF THIS FILE
---------------------
   
 * Reference
 * Authors
 * Experiments on Datasets

Reference
---------------------
A Graph Database Repository and Performance Evaluation Metrics for Graph Edit Distance, submitted to GBR2015.


Authors
---------------------
Zeina Abu-Aisheh, 3rd year PhD student at François Rabelais University, Tours, France.
Romain Raveaux, Assistant Professor at François Rabelais University, Tours, France.
Jean-Yves Ramel, Professor at François Rabelais University, Tours, France.  


Experiments on Datasets
---------------------
Three GED methods are evaluated on the aforementioned subsets. On the exact method side, A* algorithm is applied to GED problem. It is the most well-known exact method
and it is often used to evaluate the accuracy of approximate methods. On the approximate method side, one tree-based method and another assignment-based method are 
selected. For the tree-based methods, the truncated version of A*$, called BeamSearch (BS) is selected. This method is known to be one of the most accurate heuristic
from the literature. Among the assignment-based methods, the Bipartite GM (BP) is picked up. In [Riesen2009], the authors demonstrated that this upper bound is a good 
compromise between speed and accuracy. All these methods cover a large range of GED solvers. In the experiments, the parameter $x$ in \emph{BS-x}, is set to 1, 10 and
100, respectively. For performance evaluation, the metrics proposed in our paper [1] are taken into account.