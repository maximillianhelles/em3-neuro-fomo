# load_trials.R
# =============================================================================
# Loads behavioral trial data and returns one long-format tibble with the
# 25-column schema agreed in planning. Deliberately excludes the "excluded/"
# subfolder.
#
# Usage:
#   source("load_trials.R")
#   trials <- load_trials()
#   summarise_trials(trials)                # quick sanity check
# =============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(stringr)
  library(purrr)
  library(tibble)
})

# ---- Parsers ---------------------------------------------------------------

parse_chart_values <- function(s) {
  # "[1.0, 0.9993, ...]" -> numeric vector
  s <- str_remove_all(s, "^\\[|\\]$")
  as.numeric(str_split(s, ",\\s*", simplify = TRUE))
}

parse_action_kind <- function(s) {
  # "(True, 'BUY')" | "(True, 'SELL')" | "(False, None)" -> "BUY" | "SELL" | NA
  str_match(s, "'(BUY|SELL)'")[, 2]
}

label_condition <- function(position, direction) {
  case_when(
    position == "ASSET" & direction ==  1 ~ "Gain",
    position == "ASSET" & direction == -1 ~ "Loss",
    position == "CASH"  & direction ==  1 ~ "FOMO",
    position == "CASH"  & direction == -1 ~ "Relief",
    TRUE ~ NA_character_
  )
}

# ---- Block-level loader ----------------------------------------------------

load_block <- function(block_id, data_root = "data/behavioral_data") {
  block_dir <- file.path(data_root, block_id)
  files     <- list.files(block_dir, pattern = "_results_block\\.csv$",
                          full.names = TRUE)
  if (length(files) == 0L) {
    warning(sprintf("No files in %s", block_dir))
    return(tibble())
  }
  # Read all columns as character first to protect chart_values; coerce later.
  read_csv(files, show_col_types = FALSE, col_types = cols(.default = "c"))
}

# ---- Main loader -----------------------------------------------------------

load_trials <- function(data_root = "data/behavioral_data",
                        blocks = c("control", "low", "high")) {
  
  raw <- map_dfr(blocks, load_block, data_root = data_root)
  if (nrow(raw) == 0L) return(raw)
  
  raw <- raw %>%
    mutate(
      # ---- type coercions ----
      trial_num    = as.integer(trial_num),
      direction    = as.integer(direction),
      jump_index   = as.integer(jump_index),
      action_index = suppressWarnings(as.integer(action_index)),
      jump_pct     = as.numeric(jump_pct),
      action_value = suppressWarnings(as.numeric(action_value)),
      final_value  = as.numeric(final_value),
      valence      = as.integer(valence),
      arousal      = as.integer(arousal),
      regret       = as.integer(regret),
      
      # ---- parse action_taken string ----
      action_kind = parse_action_kind(action_taken),
      
      # ---- chart_values derivatives (parse once, reuse) ----
      # jump_index is 0-based (Python). In R 1-based indexing:
      #   pre-spike  value -> v[jump_index]      (last pre-spike sample)
      #   post-spike value -> v[jump_index + 1]  (first post-spike sample)
      .values             = map(chart_values, parse_chart_values),
      pre_spike_value     = map2_dbl(.values, jump_index, ~ .x[.y]),
      post_spike_value    = map2_dbl(.values, jump_index, ~ .x[.y + 1L]),
      post_spike_extremum = pmap_dbl(
        list(.values, jump_index, direction),
        function(v, j, d) {
          post <- v[(j + 1L):length(v)]
          if (d == 1L) max(post) else min(post)
        }
      ),
      
      # ---- design-derived ----
      intended_condition = label_condition(position, direction),
      
      # ---- timing ----
      # NA when no action, since action_index is NA and arithmetic propagates.
      action_before_spike = action_index < jump_index,
      action_jump_diff          = action_index - jump_index,
      
      # ---- realized condition (what the participant held at spike onset) ----
      realized_position = if_else(
        is.na(action_index) | action_index >= jump_index,
        position,        # no action, or acted after spike -> still initial
        final_position   # acted before spike -> already switched
      ),
      realized_condition = label_condition(realized_position, direction),
      condition_switched = intended_condition != realized_condition,
      
      # ---- trajectory outcome ----
      # SELLs lock in value at keypress; BUYs and no-action ride to end.
      exit_value = if_else(
        !is.na(action_kind) & action_kind == "SELL",
        action_value,
        final_value
      ),
      # Direction-neutral: 1 = full spike retained, 0 = fully erased,
      # <0 = reversed past pre-spike level, >1 = drifted past the spike.
      spike_retained = (exit_value - pre_spike_value) /
        (post_spike_value - pre_spike_value)
    ) %>%
    select(-.values) %>%
    
    # ---- factor conversions (after all derivations that need characters) ----
  mutate(
    block_id           = factor(block_id, levels = c("control", "low", "high")),
    position           = factor(position, levels = c("ASSET", "CASH")),
    realized_position  = factor(realized_position, levels = c("ASSET", "CASH")),
    intended_condition = factor(intended_condition,
                                levels = c("Gain", "Loss", "FOMO", "Relief")),
    realized_condition = factor(realized_condition,
                                levels = c("Gain", "Loss", "FOMO", "Relief")),
    action_kind        = factor(action_kind, levels = c("BUY", "SELL"))
  ) %>%
    
    # ---- final column order ----
  select(
    participant_id, block_id, trial_num, ticker,
    position, direction, intended_condition,
    jump_index, jump_pct, action_index, action_kind,
    action_before_spike, action_jump_diff,
    realized_position, realized_condition, condition_switched,
    pre_spike_value, post_spike_value, post_spike_extremum,
    exit_value, final_value, spike_retained,
    valence, arousal, regret
  )
  
  raw
}

# ---- Diagnostic ------------------------------------------------------

summarise_trials <- function(df) {
  cat("Rows:        ", nrow(df), "\n")
  cat("Participants:", length(unique(df$participant_id)), "\n\n")
  
  cat("By block x realized condition:\n")
  print(df %>% count(block_id, realized_condition))
  
  cat("\nSwitch rate by block:\n")
  print(df %>%
          group_by(block_id) %>%
          summarise(n = n(),
                    n_switched = sum(condition_switched, na.rm = TRUE),
                    switch_rate = mean(condition_switched, na.rm = TRUE),
                    .groups = "drop"))
  
  cat("\nspike_retained summary (realized Gain + Loss only):\n")
  print(df %>%
          filter(realized_condition %in% c("Gain", "Loss")) %>%
          group_by(realized_condition) %>%
          summarise(
            median_retained = median(spike_retained, na.rm = TRUE),
            mean_retained   = mean(spike_retained,   na.rm = TRUE),
            pct_fully_eroded = mean(spike_retained < 0.2, na.rm = TRUE),
            .groups = "drop"
          ))
  
  invisible(df)
}

source("analysis/post/load_trials.R")
trials <- load_trials()
summarise_trials(trials) 