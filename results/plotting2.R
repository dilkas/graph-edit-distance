library(lattice)
library(latticeExtra)

ged <- read.csv('../ged_results.csv', header = TRUE)
clique1 <- read.csv('../clique1_results.csv', header = TRUE)
clique2 <- read.csv('../clique2_results.csv', header = TRUE)
mwc <- read.csv('../mwc.csv', header = TRUE)
answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC5-lowlevelinfo.csv', header = TRUE, sep = ';')

# rows where GED and clique1 disagree
which(abs(ged$answer + clique1$answer) >= 1, arr.ind = TRUE)
# rows where clique2 and clique1 disagree
which(abs(clique1$answer - clique2$answer) >= 1, arr.ind = TRUE)

# where GED is wrong
which(abs(answers$distance - ged$answer) >= 1, arr.ind = TRUE)
# where clique1 is wrong
which(abs(answers$distance + clique1$answer) >= 1, arr.ind = TRUE)

# where clique2 is wrong
which(abs(answers$distance + clique2$answer) >= 1, arr.ind = TRUE)
# where clique2 is wrong but satisfiable
which(abs(answers$distance + clique2$answer) >= 0.1 & abs(clique2$answer - 1) >= 0.1, arr.ind = TRUE)
#where clique2 is unsatisfiable
which(abs(clique2$answer - 1) < 0.1, arr.ind = TRUE)

# where mwc differs from clique1
which(abs(mwc$answer + clique1$answer) >= 0.1, arr.ind = TRUE)
# mwc - clique1
clique1$answer - mwc$answer
summary(mwc$runtime)

max(abs(answers$distance + clique2$answer))
plot(answers$distance + clique2$answer)

runtimes = data.frame(ged = ged$runtime, clique1 = clique1$runtime, clique2 = clique2$runtime)
ecdfplot(~ ged + clique1 + clique2, data = runtimes, auto.key = list(space = 'right'), xlab = 'runtime (ms)')
