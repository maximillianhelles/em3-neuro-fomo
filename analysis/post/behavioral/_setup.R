pkgs <- c("tidyverse", "lme4", "lmerTest", "pbkrtest", "emmeans", "gt", "broom.mixed")

for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

library(tidyverse)
library(lme4)
library(lmerTest)
library(pbkrtest)
library(emmeans)

df <- read_csv("../../../data/behavioral_data/master_classified.csv", show_col_types = FALSE) |>
  mutate(
    # Internal mappings
    realized_condition = factor(realized_condition,
                                 levels = c("Gain", "Relief", "FOMO", "Loss")),
    intended_condition = factor(intended_condition,
                                 levels = c("Gain", "Relief", "FOMO", "Loss")),
    block_id           = factor(block_id, levels = c("control", "low", "high")),
  )
