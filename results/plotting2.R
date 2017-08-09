library(lattice)
library(latticeExtra)

mwc <- read.csv('../mwc.csv', header = TRUE)
cp <- read.csv('../cp.csv', header = TRUE)
answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC5-lowlevelinfo.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/CMU-GED/CMU-low-level-info/CMU-low-level-info.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/Mutagenicity-GED/Mutagenicity-low-level-info/MUTA10-lowlevelinfo.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/Protein-GED/Protein-low-level-info/Protein20-lowlevelinfo.csv', header = TRUE, sep = ';')

merged <- merge(mwc, answers, by.x = c('graph1', 'graph2'), by.y = c('Graph1.Name', 'Graph2.Name'))
filtered <- merged[merged$optimal.solution.found == 'true' & merged$distance != 0,]

# where mwc is wrong
which(abs(merged$answer - merged$distance) >= 1, arr.ind = TRUE)
summary(mwc$runtime)
plot((merged$answer - merged$distance)[merged$optimal.solution.found == 'true'])
plot(merged$answer - merged$distance)
optimal <- answers[answers$optimal == 'true', ]

runtimes = data.frame(ged = ged$runtime, clique1 = clique1$runtime, clique2 = clique2$runtime)
ecdfplot(~ ged + clique1 + clique2, data = runtimes, auto.key = list(space = 'right'), xlab = 'runtime (ms)')

# are some of the graph combinations tested multiple times?
which(duplicated(answers[, c('Graph1.Name', 'Graph2.Name')]))
