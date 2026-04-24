library(tidyverse)

data <- read_csv("data/stimuli_validation/validation_results.csv")

n <- nrow(data)

correct <- sum(data$correct) / n
incorrect <- 1-correct

cat(sprintf("Split is %.2f%% / %.2f%%", correct*100, incorrect*100))
p <- 0.5
result <- binom.test(sum(data$correct), n, p)

print(result)

if (result$conf.int[1] <= p & p <= result$conf.int[2]) {
  cat("Not significantly different from chance")
} else {
  cat("Significantly different from chance")
}