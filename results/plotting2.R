cp <- read.csv('../CP_results.csv', header = TRUE)
clique <- read.csv('clique_results.csv', header = TRUE)

plot(clique$runtime - cp$runtime, ylab = 'CP runtime - clique runtime')
abline(0, 0)

plot(cp$runtime, col = 'red', ylab = 'runtime (ms)', main = 'Original CP model (red) vs Clique(ish) Encoding (green)')
points(clique$runtime, col = 'green')

max(cp$answer + clique$answer)
min(cp$answer + clique$answer)
