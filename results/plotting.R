data <- read.csv('../results.csv', header = TRUE)
data$color = 'red'
data$color[data$times_satisfiable >= 2] = 'green'
plot(data$P, data$t, col = data$color, xlab = 'P(edge)', ylab = 't', main = '40 vertices, 3 repetitions, 8 colors')
