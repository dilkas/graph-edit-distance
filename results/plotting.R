mcis <- read.csv('../mcis.csv', header = TRUE)
mc <- read.csv('../mc.csv', header = TRUE)

title = "15 vertices, P(edge) = 0.5, P(label) = 0.3"
plot(mcis$l, mcis$runtime, type = 'l', xlab = 'P(label)', ylab = 'runtime', main = title)
lines(mc$l, mc$runtime, col = 'blue')
legend('topright', c('MCIS', 'MC'), lty = c(1, 1), col = c('black', 'blue'))
