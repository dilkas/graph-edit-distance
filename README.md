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
2. Run `make convert-model`, where `model` is one of: `cp`, `vertex-edge-weights`, `vertex-weights`, `mwc`. The first three are MiniZinc models, the last one is a C program. This converts the pairs of graphs mentioned in the `INFO_FILE` into either DZN or DIMACS format for the appropriate model. Note that if a generated file already exists, it will NOT be overwritten.
3. Run `make model` (for the same value of `model`) and results will be gradually written to `model.csv`. Use `-j` and `-l` flags to run multiple different problem instances in parallel.
4. Modify and use `results/plotting2.R` as needed to extract meaningful information from the data.

`make clean` can be used to remove all the generated files: DZN, CSV, and everything created by any of the 'convert' targets. If you run a `make model` command several times, the results file will be overwritten.