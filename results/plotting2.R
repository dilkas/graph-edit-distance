ged <- read.csv('../ged_results.csv', header = TRUE)
clique1 <- read.csv('../clique1_results.csv', header = TRUE)
clique2 <- read.csv('../clique2_results.csv', header = TRUE)
answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC5-lowlevelinfo.csv', header = TRUE, sep = ';')

plot(clique1$runtime - ged$runtime, ylab = 'clique1 runtime - GED runtime')
abline(0, 0)

plot(ged$runtime, col = 'red', ylab = 'runtime (ms)', main = '')
points(clique1$runtime, col = 'green')

# rows where the two algorithms disagree
which(abs(ged$answer + clique1$answer) >= 1, arr.ind = TRUE)
# where GED is wrong
which(abs(answers$distance - ged$answer) >= 1, arr.ind = TRUE)
# where clique1 is wrong
which(abs(answers$distance + clique1$answer) >= 1, arr.ind = TRUE)
# where clique2 is wrong
which(abs(answers$distance + clique2$answer) >= 1, arr.ind = TRUE)
