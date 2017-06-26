data <- read.csv('../results.csv', header = TRUE)

data$color = 'red'
data$color[data$satisfiable >= 0.5] = 'green'

data$constraints = 4950 * (1 - data$P) + 1
data$prediction = data$nodes * data$constraints
#data$prediction <- data$prediction * mean(data$runtime)/mean(data$prediction)

plot(data$P, data$prediction, type = 'l', col = 'blue', xlab = 'P(edge)', ylab = 'runtime')
plot(data$P, data$runtime, col = data$color, xlab = 'P(edge)', ylab = 'runtime', main = '100 vertices, 10 repetitions, clique size = 10')

plot(data$P, data$nodes, col = data$color, xlab = 'P(edge)', ylab = 'nodes', main = '100 vertices, 10 repetitions, clique size = 10')
#plot(data$P, data$solvetime, col = data$color, xlab = 'P(edge)', ylab = 'solvetime', main = '100 vertices, 10 repetitions, clique size = 10')

fit <- lm(runtime ~ prediction + nodes + constraints, data = data)
lines(data$P, -6.686 + 4.069e-05 * data$prediction - 7.572e-02 * data$nodes + 2.289e-02 * data$constraints, col = 'blue')
summary(fit)
plot(fit)
