ged <- read.csv('../ged_results.csv', header = TRUE)
clique1 <- read.csv('../clique1_results.csv', header = TRUE)
clique2 <- read.csv('../clique2_results.csv', header = TRUE)
answers <- read.csv('../graphs/db/GREC-GED/GREC-low-level-info/GREC5-lowlevelinfo.csv', header = TRUE, sep = ';')

plot(clique1$runtime - ged$runtime, ylab = 'clique1 runtime - GED runtime')
abline(0, 0)

plot(ged$runtime, t = 'l', ylab = 'runtime (ms)', main = '100 pairs of GREC 5-vertex graphs')
lines(clique1$runtime, col = 'red')
lines(clique2$runtime, col = 'green')
legend('topleft', c('GED', 'clique1', 'clique2'), lty = c(1, 1, 1), col = c('black', 'red', 'green'))

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

max(abs(answers$distance + clique2$answer))
plot(answers$distance + clique2$answer)
