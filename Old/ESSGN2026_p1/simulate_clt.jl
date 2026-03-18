using Random, Distributions, CairoMakie

Random.seed!(2026)

# -------------------------------------------------------------------
# Simulate genetic values  g_i = Σ_j β_j x_{ij}  for different M
# Under the infinitesimal scaling: β_j ~ N(0, σ²_g / M)
# Genotypes x_{ij} ~ {0, 1, 2} with allele freq p = 0.5
# -------------------------------------------------------------------

N = 50_000          # number of individuals
σ²_g = 1.0          # total genetic variance (target)
M_values = [3, 5, 100]

fig = Figure(size = (1100, 500))

for (idx, M) in enumerate(M_values)
    ax = Axis(fig[1, idx],
              title  = "M = $M loci",
              xlabel = "Genetic value (g)",
              ylabel = idx == 1 ? "Density" : "")

    # Draw effect sizes with infinitesimal scaling
    β = rand(Normal(0, sqrt(σ²_g / M)), M)

    # Draw genotypes: Binomial(2, 0.5) → {0, 1, 2}
    X = rand(Binomial(2, 0.5), N, M)

    # Genetic values
    g = X * β          # N-vector

    # Centre for display (remove mean from genotype coding)
    g .= g .- mean(g)

    # Histogram
    hist!(ax, g, bins = 60, normalization = :pdf,
          color = (:steelblue, 0.55), strokewidth = 0.3, strokecolor = :white)

    # Overlay normal density with matched mean & std
    xs = range(minimum(g), maximum(g), length = 300)
    lines!(ax, xs, pdf.(Normal(0, std(g)), xs),
           color = :firebrick, linewidth = 2.5)
end

# Shared super-title
Label(fig[0, :], 
      "Convergence to normality as number of causal loci (M) increases",
      fontsize = 16, font = :bold)

save("clt_convergence.png", fig, px_per_unit = 3)
println("Saved clt_convergence.png")
