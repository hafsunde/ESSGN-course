using LinearAlgebra
using Distributions
using DataFrames
using GLM
using GREMLModels
using Random

Random.seed!(080318)

t0 = time()

# Session 1 practical recap
# ----------------------------------------
# 1. Simulate genotypes
# ----------------------------------------
N, M = 3000, 12000  # trios and SNPs
p = 0.5

Xf = rand(Bernoulli(p), N, M) .+ rand(Bernoulli(p), N, M)
Xm = rand(Bernoulli(p), N, M) .+ rand(Bernoulli(p), N, M)
Xo = rand.(Bernoulli.(Xf ./ 2)) .+ rand.(Bernoulli.(Xm ./ 2))
X = vcat(Xf, Xm, Xo)

idf = 1:N
idm = N+1:2N
ido = 2N+1:3N

# 2. Simulate phenotypes
# ----------------------------------------
p̂ = vec(mean(X, dims = 1)) ./ 2
mx = 2 .* p̂
sdx = sqrt.(mx .* (1 .- p̂))
X̃ = Float64.(X)
X̃ .-= mx'
X̃ ./= sdx'

σ²g = 0.5
σ²e = 0.5
b = randn(M) * √(σ²g / M)
g = X̃ * b
e = randn(3 * N) * √(σ²e)
y = g + e

# Inspect correlation/covariance in genetic values (father, mother, offspring)
Gc = hcat(g[idf], g[idm], g[ido])
cor(Gc)
cov(Gc)

# 3. Parent-offspring regression
# ----------------------------------------
yp = 0.5 * (y[idf] + y[idm])
yo = y[ido]
df1 = DataFrame(yo = yo, yp = yp)
mpo = lm(@formula(yo ~ yp), df1)
mpo

# 4. GREML direct model
# ----------------------------------------
# Compute the grm
# This is time consuming 
# Use the time to think about what the code does
G = G = (X̃ * X̃') / M

# The block of the grm corresponding to offspring
Goo = G[ido, ido]
Id = Diagonal(ones(N))
r = [Goo, Id]
mdirect = fit(GREMLModel, @formula(yo ~ 1), df1, r; verbose = false)

# Session 2 extension: maternal IGE / M-GCTA
# ----------------------------------------
# 5. Simulate offspring phenotype with maternal IGE component
# ----------------------------------------
Σg = [0.2 0.2; 0.2 0.5]
σ²e = 0.1
C = cholesky(Symmetric(Σg / M)).U
B = randn(M, 2) * C
g_m = X̃ * B[:, 1]
g_d = X̃ * B[:, 2]
e = g_m[idm] + randn(N) * √(σ²e)
yo2 = g_d[ido] + e

# 6. Fit the (wrong) direct model again
# ----------------------------------------
df2 = DataFrame(y = yo2)
mdirect2 = fit(GREMLModel, @formula(y ~ 1), df2, r; verbose = false)

# 7. Fit the maternal IGE model
# ----------------------------------------
Gmm = G[idm, idm]
Dom = G[ido, idm] + G[idm, ido]
r = [Gmm, Dom, Goo, Id]
mmaternal = fit(GREMLModel, @formula(y ~ 1), df2, r; verbose = false)

elapsed = time() - t0
