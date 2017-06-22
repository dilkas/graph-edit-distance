data <- read.csv('../results.csv', header = TRUE)
data$color = 'red'
data$color[data$times_satisfiable >= 2] = 'green'
plot(data$P, data$t, col = data$color, xlab = 'P(edge)', ylab = 't', main = '100 vertices, 10 repetitions, clique size = 10')
