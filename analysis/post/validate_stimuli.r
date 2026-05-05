library(tidyverse)
library(BayesFactor)

data <- read_csv("data/stimuli_validation/validation_results.csv")

n <- nrow(data)
k <- sum(data$correct)

# Sample proportion
correct_prop <- k / n
incorrect_prop <- 1-correct_prop

cat(sprintf("Split is %.2f%% / %.2f%%", correct_prop*100, incorrect_prop*100))

# --- FREQUENTIST BINOMIAL ANALYSIS ---
result <- binom.test(k, n, p=0.5)
result

# --- BAYESIAN CONJUGATE UPDATING ---
# Assume θ is distributed as Beta(1,1) / uniform.
alpha_prior <- 1
beta_prior  <- 1

# Successes k accumulate into α, failures n-k accumulate into β.
# Given data, the distribution shifts: θ|Data ∼ Beta(alpha + k, beta + n - k)
alpha_post <- alpha_prior + k
beta_post  <- beta_prior + (n - k)

# Standard mean of a Beta distribution:
post_mean <- alpha_post / (alpha_post + beta_post)

# Credibility interval - qbeta is the inverse cumulative distribution function ("F^{-1}")
# meaning it returns two bounds that "cut off" 0% to 2.5% and 97.5% to 100%.
ci        <- qbeta(c(0.025, 0.975), alpha_post, beta_post)

# Posterior probability of being above chance
p <- 0.5
p_above_chance <- 1 - pbeta(p, alpha_post, beta_post)

cat(sprintf("Posterior mean:        %.4f\n", post_mean))
cat(sprintf("95%% credible interval: [%.4f, %.4f]\n", ci[1], ci[2]))
cat(sprintf("P(theta > 0.5 | data): %.4f\n", p_above_chance))

if (ci[1] <= p & p <= ci[2]) {
  cat("0.5 is inside the 95% credible interval: not credibly different from chance.\n")
} else {
  cat("0.5 is outside the 95% credible interval: credibly different from chance.\n")
}

bf10 <- proportionBF(y = k, N = n, p = 0.5)
bf01 <- 1 / bf10
print(bf01)

bf01_value <- extractBF(bf01)$bf
cat(sprintf("Data is %.4f times more likely under H0 (θ = 0.5) than H1.\n",
            bf01_value))