rm(list = ls())

set.seed(080318)

library(gaston)

# 1. Sim genotypes
# ----------------------------------------
N <- 3000 # Trios
M <- 12000 # Snps
p <- 0.5
Xf <- matrix(rbinom(N * M, 2, p), N, M)
Xm <- matrix(rbinom(N * M, 2, p), N, M)
Xo <- matrix(
  rbinom(N * M, 1, as.vector(Xf) / 2) + rbinom(N * M, 1, as.vector(Xm) / 2),
  N, M
)
X <- rbind(Xf, Xm, Xo)

idf <- 1:N
idm <- (N + 1):(2 * N)
ido <- (2 * N + 1):(3 * N)

# 2. Sim phenotypes
# ----------------------------------------
pest <- colMeans(X) / 2
Xtilde <- scale(X, 2 * pest, sqrt(2 * pest * (1 - pest)))
s2g <- 0.5
s2e <- 0.5
b <- rnorm(M, 0, sqrt(s2g / M))
g <- as.vector(Xtilde %*% b)
e <- rnorm(3 * N, 0, sqrt(s2e))
y <- g + e

# This is a good time to look at the corr/cov in genetic values
Gc <- cbind(g[idf], g[idm], g[ido])
cor(Gc)
cov(Gc)

# 3. Parent-offspring regression
# ----------------------------------------
yp <- 0.5 * (y[idf] + y[idm])
yo <- y[ido]
mpo <- lm(yo ~ yp)
summary(mpo)

# 4. GREML direct model
# ----------------------------------------
# Compute the grm
# This is time consuming
# Use the time to think about what the code does
G <- tcrossprod(Xtilde) / M

# The block of the grm corresponding to offspring
Goo <- G[ido, ido]
mdirect <- lmm.aireml(yo, K = Goo, verbose = FALSE)
mdirect$tau

# 5. Simulate with a maternal ige
# ----------------------------------------
Sg <- rbind(
  c(0.2, 0.2),
  c(0.2, 0.5)
)
s2e <- 0.1
B <- matrix(rnorm(2 * M), M, 2) %*% chol(Sg / M)
gm <- Xtilde %*% B[, 1]
gd <- Xtilde %*% B[, 2]
e <- gm[idm] + rnorm(N, 0, sqrt(s2e))
yo2 <- gd[ido] + e

# 6. Fit the (wrong) direct model again
# ----------------------------------------
mdirect2 <- lmm.aireml(yo2, K = Goo, verbose = FALSE)
mdirect2$tau

# 7. Fit the maternal ige model
# ----------------------------------------
Gmm <- G[idm, idm]
Dom <- G[ido, idm] + G[idm, ido]
mmaternal <- lmm.aireml(yo2, K = list(Gmm, Dom, Goo), verbose = FALSE)
mmaternal$tau
