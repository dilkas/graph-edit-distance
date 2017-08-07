Supported problems:
* max clique (optimization & decision),
* subgraph isomorphism,
* maximum common induced subgraph and its encoding as max clique for labelled and unlabelled graphs,
* graph edit distance (GED):
    * a constraint programming model,
    * 2 encodings as minimum weight clique:
        * with weights on vertices,
        * with weights on both vertices and edges.

# How to run a non-GED experiment

1. Set the relevant parameters at the top of Makefile.
2. Make sure the MiniZinc models listed as prerequisites of some of the targets are set correctly.
3. Run `make target` for your selected target. The results will be gradually written to either `clique.csv` or `subgraph.csv` or both, depending on the target.
4. Modify `results/plotting.R` as needed to extract meaningful information from the data.

# How to run a GED experiment

1. Set the relevant parameters at the top of Makefile. `DATABASE` can be one of: `CMU`, `GREC`, `Mutagenicity`, `Protein`.
2. Run `make convert-model`, where `model` is one of: `cp`, `vertex-edge-weights`, `vertex-weights`, `mwc`. The first three are MiniZinc models, the last one is a C program. This converts the pairs of graphs mentioned in the `INFO_FILE` into either DZN or DIMACS format for the appropriate model.
3. Run `make model` (for the same value of `model`) and results will be gradually written to `model.csv`.
4. Modify and use `results/plotting2.R` as needed to extract meaningful information from the data.
