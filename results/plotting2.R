library(lattice)
library(latticeExtra)

grec15 <- read.csv('grec15.csv', header = TRUE)
grecmix <- read.csv('grecmix.csv', header = TRUE)
muta20 <- read.csv('muta20.csv', header = TRUE)
protein20 <- read.csv('protein20.csv', header = TRUE)

mwc <- read.csv('../mwc.csv', header = TRUE)
cp <- read.csv('../cp.csv', header = TRUE)
vertex_weights <- read.csv('../vertex-weights.csv', header = TRUE)
vertex_edge_weights <- read.csv('../vertex-edge-weights.csv', header = TRUE)

answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC15-lowlevelinfo.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/CMU-GED/CMU-low-level-info/CMU-low-level-info.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/Mutagenicity-GED/Mutagenicity-low-level-info/MUTA10-lowlevelinfo.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/Protein-GED/Protein-low-level-info/Protein20-lowlevelinfo.csv', header = TRUE, sep = ';')

merged <- merge(grec15, answers, by.x = c('graph1', 'graph2'), by.y = c('Graph1.Name', 'Graph2.Name'))
filtered <- merged[merged$optimal.solution.found == 'true',]
deviations <- abs(filtered$answer - filtered$distance)/filtered$distance
deviations[is.nan(deviations)] <- 0
summary(deviations)
deviations <- deviations[deviations != 0]

# where mwc is wrong
which(abs(merged$answer - merged$distance) >= 1, arr.ind = TRUE)
summary(mwc$runtime)
plot((merged$answer - merged$distance)[merged$optimal.solution.found == 'true'])
plot(merged$answer - merged$distance)
optimal <- answers[answers$optimal == 'true', ]

runtimes = data.frame(cp = cp$runtime, vertex_weights = vertex_weights$runtime, vertex_edge_weights = vertex_edge_weights$runtime)
ecdfplot(~ cp + vertex_weights + vertex_edge_weights, data = runtimes, auto.key = list(space = 'right'), xlab = 'runtime (ms)')
runtimes = data.frame(grec_mix = grecmix$runtime, grec15 = grec15$runtime, muta20 = muta20$runtime, protein20 = protein20$runtime)
ecdfplot(~ grec_mix + grec15 + muta20 + protein20, data = runtimes, auto.key = list(space = 'right'), xlab = 'runtime (ms)')

# are some of the graph combinations tested multiple times?
which(duplicated(answers[, c('Graph1.Name', 'Graph2.Name')]))
