proof <- read.csv('proof.csv', header = TRUE)
total <- read.csv('total.csv', header = TRUE)

merged <- merge(proof, total, by = c('graph1', 'graph2'))
merged <- merged[merged$runtime.y < 1000 & merged$answer.y > 0,]
plot(merged$runtime.x, merged$runtime.y - merged$runtime.x, xlab = 'proof time', ylab = 'search time', main = 'Search time vs proof time')
