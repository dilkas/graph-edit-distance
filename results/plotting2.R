library(lattice)
library(latticeExtra)

mwc <- read.csv('../grec.csv', header = TRUE)
answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC15-lowlevelinfo.csv', header = TRUE, sep = ';')
answers <- read.csv('../graphs/db/CMU-GED/CMU-low-level-info/CMU-low-level-info.csv', header = TRUE, sep = ';')

# where mwc is wrong
which(abs(mwc$answer - answers$distance) >= 1, arr.ind = TRUE)
summary(mwc$runtime)
plot((mwc$answer - answers$distance)[answers$optimal.solution.found == 'true'])

runtimes = data.frame(ged = ged$runtime, clique1 = clique1$runtime, clique2 = clique2$runtime)
ecdfplot(~ ged + clique1 + clique2, data = runtimes, auto.key = list(space = 'right'), xlab = 'runtime (ms)')
