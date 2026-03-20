# Remove everything from the current R workspace.
# This makes the script start from a clean environment so that old objects
# do not accidentally affect the results.
rm(list = ls())

# Set the random seed so that the simulation is reproducible.
# Anyone running the script with the same seed should get the same random draws.
set.seed(080318)

# Load the gaston package.
# This package contains functions for genetic data analysis, including
# linear mixed models used later in the script.
library(gaston)

# Session 1

# Record the current time so we can measure how long the whole script takes.
tme <- Sys.time()

# 1. Sim genotypes
# ----------------------------------------

# Number of families (trios) to simulate.
# Each trio consists of father, mother, and offspring.
N <- 3000 # Trios

# Number of SNPs (genetic variants) to simulate for each person.
M <- 12000 # Snps

# Minor/reference allele frequency used in the simulation.
# Here every SNP is simulated with allele frequency 0.5 for simplicity.
p <- 0.5

# Simulate fathers' genotypes.
# rbinom(N * M, 2, p) draws N*M genotype values from a Binomial(2, p),
# which gives values 0, 1, or 2 corresponding to genotype counts.
# matrix(..., N, M) reshapes the long vector into an N x M matrix:
#   rows = individuals
#   columns = SNPs
Xf <- matrix(rbinom(N * M, 2, p), N, M)

# Simulate mothers' genotypes in the same way as fathers.
Xm <- matrix(rbinom(N * M, 2, p), N, M)

# Simulate offspring genotypes by Mendelian inheritance.
# For each SNP in each trio:
#   - the offspring gets one allele from the father
#   - and one allele from the mother
#
# as.vector(Xf) / 2 converts genotype counts 0/1/2 into probabilities
# of transmitting the reference allele: 0, 0.5, or 1.
#
# rbinom(N * M, 1, as.vector(Xf) / 2) simulates the paternal transmitted allele:
#   0 = father transmits the non-reference allele
#   1 = father transmits the reference allele
#
# The same is done for the mother, and the two transmitted alleles are summed,
# giving offspring genotypes coded 0, 1, or 2.
#
# Finally, matrix(..., N, M) reshapes this into an N x M offspring genotype matrix.
Xo <- matrix(
  rbinom(N * M, 1, as.vector(Xf) / 2) + rbinom(N * M, 1, as.vector(Xm) / 2),
  N, M
)

# Stack fathers, mothers, and offspring into one large genotype matrix.
# The resulting matrix has 3N rows:
#   first N rows     = fathers
#   next N rows      = mothers
#   final N rows     = offspring
X <- rbind(Xf, Xm, Xo)

# Create row indices for fathers inside the stacked matrix X.
idf <- 1:N

# Create row indices for mothers inside X.
idm <- (N + 1):(2 * N)

# Create row indices for offspring inside X.
ido <- (2 * N + 1):(3 * N)

# 2. Sim phenotypes
# ----------------------------------------

# Estimate allele frequencies from the simulated data.
# Since genotypes are coded 0/1/2, dividing the mean genotype by 2 gives
# the estimated reference allele frequency at each SNP.
pest <- colMeans(X) / 2

# Standardize the genotype matrix SNP-wise.
# For each SNP, subtract the expected genotype mean 2p
# and divide by the standard deviation sqrt(2p(1-p)).
#
# This is the standard genotype scaling often used in GREML / SNP-heritability work.
# The result is a standardized genotype matrix where columns are approximately
# mean 0 and variance 1.
Xtilde <- scale(X, 2 * pest, sqrt(2 * pest * (1 - pest)))

# Set the additive genetic variance in the phenotype.
s2g <- 0.5

# Set the environmental/residual variance in the phenotype.
s2e <- 0.5

# Simulate SNP effect sizes.
# Each SNP effect is drawn from a normal distribution with mean 0 and variance s2g / M.
# This implies that, in expectation, the total additive genetic variance across SNPs
# sums to about s2g.
b <- rnorm(M, 0, sqrt(s2g / M))

# Compute each individual's additive genetic value.
# Xtilde %*% b is the polygenic score / additive genetic component obtained by
# summing standardized genotypes weighted by their SNP effects.
# as.vector() converts the matrix result into a simple numeric vector of length 3N.
g <- as.vector(Xtilde %*% b)

# Simulate environmental noise for all 3N individuals.
# This is independent residual variation not explained by genotype.
e <- rnorm(3 * N, 0, sqrt(s2e))

# The phenotype is the sum of genetic value and environmental noise.
# Since s2g = 0.5 and s2e = 0.5, the total variance should be about 1.
y <- g + e

# This is a good time to look at the corr/cov in genetic values

# Extract the genetic values for fathers, mothers, and offspring into a 3-column matrix.
# Each row corresponds to one family:
#   column 1 = father's genetic value
#   column 2 = mother's genetic value
#   column 3 = offspring's genetic value
Gc <- cbind(g[idf], g[idm], g[ido])

# Compute the correlation matrix among father, mother, and offspring genetic values.
# Under random mating and additive inheritance, you would expect:
#   - father/mother correlation near 0
#   - parent/offspring correlation around 0.5
cor(Gc)

# Compute the covariance matrix among father, mother, and offspring genetic values.
# Same structure as above, but in covariance rather than standardized correlation units.
cov(Gc)

# 3. Parent-offspring regression
# ----------------------------------------

# Compute the mid-parent phenotype:
# the average of father and mother phenotypes in each family.
# This is the standard predictor in classical parent-offspring regression.
yp <- 0.5 * (y[idf] + y[idm])

# Extract offspring phenotypes.
yo <- y[ido]

# Fit a linear regression of offspring phenotype on mid-parent phenotype.
# In classical quantitative genetics, the slope of offspring on mid-parent
# is expected to estimate narrow-sense heritability under ideal assumptions.
mpo <- lm(yo ~ yp)

# Print the regression summary.
# The coefficient for yp is the key quantity of interest.
summary(mpo)

# 4. GREML direct model
# ----------------------------------------

# Compute the genomic relationship matrix (GRM).
# tcrossprod(Xtilde) computes Xtilde %*% t(Xtilde), i.e. pairwise genetic similarity
# between all individuals across all standardized SNPs.
# Dividing by M averages over SNPs.
#
# The result is a 3N x 3N matrix G where:
#   G[i, j] measures genomic similarity between individuals i and j.
#
# This is time consuming because the matrix is large.
G <- tcrossprod(Xtilde) / M

# Extract the offspring-offspring block of the GRM.
# This keeps only genomic relationships among offspring.
Goo <- G[ido, ido]

# Fit a direct GREML model to offspring phenotypes using only offspring GRM.
# lmm.aireml() fits a linear mixed model by average-information REML.
# Here:
#   yo = offspring phenotypes
#   K = Goo is the covariance structure induced by additive genetic similarity
#
# The model is roughly:
#   yo = genetic random effect + residual
#
# This estimates variance components associated with Goo and residual error.
mdirect <- lmm.aireml(yo, K = Goo, verbose = FALSE)

# Print the estimated variance components from the direct GREML model.
# In this simple simulation, this should recover something close to the
# direct additive genetic variance and residual variance.
mdirect$tau



# Session 2


# 5. Simulate with a maternal ige
# ----------------------------------------

# Define the covariance matrix for two sets of SNP effects:
#   column 1 effects = maternal indirect genetic effects
#   column 2 effects = offspring direct genetic effects
#
# So:
#   Var(maternal effects) = 0.2
#   Var(direct effects)   = 0.5
#   Covariance            = 0.2
#
# This means SNPs affecting the maternal indirect pathway and offspring direct pathway
# are positively correlated.
Sg <- rbind(
  c(0.2, 0.2),
  c(0.2, 0.5)
)

# Set residual variance for the new phenotype simulation.
s2e <- 0.1

# Simulate M pairs of correlated SNP effects.
# rnorm(2 * M) generates 2M independent standard normal draws.
# matrix(..., M, 2) reshapes them into an M x 2 matrix.
# %*% chol(Sg / M) induces the desired covariance structure across the two columns.
#
# The result B is an M x 2 matrix:
#   B[,1] = SNP effects for maternal indirect effects
#   B[,2] = SNP effects for offspring direct effects
B <- matrix(rnorm(2 * M), M, 2) %*% chol(Sg / M)

# Compute the maternal indirect genetic score for every individual.
# Later, only mothers' values are used as environmental input to offspring.
gm <- Xtilde %*% B[, 1]

# Compute the direct genetic score for every individual.
gd <- Xtilde %*% B[, 2]

# Construct the offspring environmental term for the new phenotype.
# This is the key indirect genetic effect part:
#   e = maternal genetic value + residual noise
#
# gm[idm] extracts maternal indirect genetic values for the mothers in each trio,
# so each offspring's environment depends on its mother's genotype-derived score.
e <- gm[idm] + rnorm(N, 0, sqrt(s2e))

# Construct the offspring phenotype under this new model.
# The phenotype now has:
#   - a direct genetic component from the offspring's own genotype: gd[ido]
#   - an indirect maternal genetic component entering through e
yo2 <- gd[ido] + e

# 6. Fit the (wrong) direct model again
# ----------------------------------------

# Fit the same offspring-only GREML model as before, but now to phenotypes
# that also contain maternal indirect genetic effects.
#
# This model is "wrong" because it assumes all genotype-related variance comes
# from the offspring's own direct genetic effects.
# In reality, some of the variation comes from maternal genotypes shaping the
# offspring environment.
mdirect2 <- lmm.aireml(yo2, K = Goo, verbose = FALSE)

# Print the variance component estimates from the misspecified direct model.
# Comparing this to the truth can show how indirect genetic effects bias
# a simple direct GREML analysis.
mdirect2$tau

# 7. Fit the maternal ige model
# ----------------------------------------

# Extract the mother-mother block of the GRM.
# This captures genomic similarity among mothers.
Gmm <- G[idm, idm]

# Construct a covariance component linking offspring phenotypes to maternal genotypes.
# G[ido, idm] is the offspring-by-mother genomic similarity matrix.
# G[idm, ido] is its transpose.
#
# Their sum creates a symmetric matrix intended to model the covariance arising
# from the overlap/correlation between offspring direct and maternal indirect
# genetic effects.
Dom <- G[ido, idm] + G[idm, ido]

# Fit a richer mixed model with three covariance components:
#   1. Gmm  = maternal indirect genetic variance component
#   2. Dom  = covariance between maternal indirect and offspring direct effects
#   3. Goo  = offspring direct genetic variance component
#
# This is the appropriately specified model for the way yo2 was simulated.
mmaternal <- lmm.aireml(yo2, K = list(Gmm, Dom, Goo), verbose = FALSE)

# Print the estimated variance components from the maternal indirect genetic effect model.
# These should correspond roughly to:
#   maternal indirect variance,
#   direct-indirect covariance,
#   direct variance,
# plus residual variance.
mmaternal$tau

# Compute total elapsed time since the start of the script.
tme <- Sys.time() - tme

# Print total runtime.
tme