mcis <- read.csv('../mcis.csv', header = TRUE)
mc <- read.csv('../mc.csv', header = TRUE)

title = "10, 10 vertices, P(edge) = 0.5"
plot(mcis$P, mcis$runtime, type = 'l', xlab = 'P(edge)', ylab = 'runtime', main = title)
lines(mc$P, mc$runtime, col = 'blue')
legend('topright', c('MCIS', 'MC'), lty = c(1, 1), col = c('black', 'blue'))
