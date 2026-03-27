# Experimental Methods 3: Neurological Responses to Controlled Financial Volatility and Counterfactual Regret

For full transparency, this repository contains all files relevant to the author's project in Experimental Methods 3 and contains all necessary files to replicate it as well as the code used for data processing. Additionally, the associated paper and this README will offer insights, discussions, and conclusions in regards to flaws, validity, and future studies.

## Objective

This study's objective is to investigate Event-Related Potentials (ERPs) associated with sudden financial volatility as well as bi-directional counterfactual outcomes (e.g., 'Fear of Missing Out' on gains vs. 'Relief' from avoiding losses). Using a Jump-Diffusion model to simulate stochastic stock movements, we time-lock EEG recordings to discrete market 'shocks,' observing how neural responses scale with real monetary risk, foregone alternatives, and participant-driven behavioral choices.

## Experimental Setup & Environment

- **Recording:** A (num-of-electrodes) EEG-headset.
- **Faraday Cage:** Experiments were conducted within the Faraday Cage to minimize external electromagnetic noise.
- **Stimulus Display:** A continuous line chart mimicking the price fluctuations of a fictional financial asset, displayed alongside real-time portfolio values for both the chosen position and its counterfactual alternative. The chart y-axis is fixed ([85:115]) to ensure that GBM noise remains visually subordinate to the experimentally induced volatility spikes.

## The Stimulus

- **Base Action:** The base fluctuations of the asset were determined by Geometric Brownian Motion, using parameters empirically estimated from the S&P-500 index. Visit `stimuli/backend/jmp_diff_model.py` for stimulus implementation, `analysis/pre/gbm_params.py` for parameter estimation logic, and `config/params.yaml` for actual parameters.
- **Spikes:** At randomized points within 10% and 90% of the trial duration, the model introduces sudden volatility in a direction predetermined by condition assignment, mimicking volatility spikes that frequently occur in real markets (e.g. following a company's earnings release).
- **Behavioral Agency:** To induce genuine emotional investment while preserving experimental control, participants began each trial with a predetermined position — either holding an asset or holding cash — and were given the option to act on it during the trial. In asset trials, participants could elect to sell their holding at any point, forfeiting the right to re-enter. In cash trials, participants could elect to purchase the asset, after which the position was held until trial end, at which point its asset value was converted to cash. This design leverages the endowment effect and genuine decision-making agency to elicit loss aversion and counterfactual regret, while maintaining full experimental control over spike direction. The participant's buy/sell decision constitutes a behavioral variable that is analysed as a moderator of ERP responses.
- **Real-Time Counterfactual Display:** During each trial, participants could observe both their actual portfolio value and the value of the unchosen alternative updating in real time alongside the chart. This continuous counterfactual exposure was designed to strengthen the affective magnitude of FOMO and relief responses. Portfolio values were displayed in peripheral vision to minimize interference with spike-locked ERP components.
- **Inter-Trial Recovery:** A 10-second fixation cross was presented between successive trials to allow for affective baseline restoration. This interval serves as a washout period, neutralizing the psychological impact of prior market shocks and preventing carryover effects between trials.

## Design & Incentivization

The experiment was divided into three separate blocks:

- **Block 1 — Control:** Participants merely observed the movements of the graph with no capital at stake.
- **Block 2 — DKK 50:** Given 50 DKK capital per trial.
- **Block 3 — DKK 100:** Given 100 DKK capital per trial.

Block order was counterbalanced across participants for blocks 2 and 3. Concluding the experiment, the participant received the monetary outcome of a randomly selected trial from either block two or three. This incentive structure was designed to ensure genuine activation of the brain's mesolimbic pathways. Due to the anticipated low sample size, the experiment was designed as a within-subject design.

Across the 40 trials, participants held an asset position in 20 and a cash position in the remaining 20, with initial values of 0, 50, or 100 DKK assigned per trial.

## Conditions

Conditions are defined by the intersection of initial position and spike direction, both of which are experimentally controlled. The participant's buy/sell decision during the trial determines the *realized* condition experienced at the time of the spike.

|                   | Positive Spike       | Negative Spike        |
|-------------------|----------------------|-----------------------|
| **Invested**      | Condition A: Gain    | Condition B: Loss     |
| **Not Invested**  | Condition C: FOMO    | Condition D: Relief   |

Spike direction was predetermined across trials (20 upward, 20 downward) and randomization applied only to spike timing within each trial (between 10% and 90% of trial duration). Initial position was likewise controlled (20 asset, 20 cash). The participant's choice to buy or sell prior to the spike shifts their realized condition; for example, selling before a negative spike converts a Loss (B) outcome into a FOMO (C) outcome. This behavioral split is treated as a moderating variable in the ERP analysis rather than a design factor. Conditions were strictly counterbalanced across trials within each block to ensure equal base representation.

## Trial Flow

1. **Position disclosure** — participant is informed whether they hold the asset or cash for this trial
2. **GBM trial** — chart runs with real-time portfolio values displayed for both actual and counterfactual positions; participant may buy or sell at any point; spike occurs at a randomized point
3. **SAM rating** — participant rates current valence and arousal using the Self-Assessment Manikin scale
4. **Fixation cross** — 10-second inter-trial interval

## Neurological Markers

The analysis will focus on the two primary ERPs known to be present in such tasks:

- **The P300 Wave:** A positive-going deflection occurring approximately 300–600ms post-stimulus, primarily distributed over the parietal scalp. In this study, the P300 serves as an index of salience and context updating, expected to scale with the surprise element of the Jump-Diffusion spikes. We hypothesize that P300 amplitudes will be significantly larger in high-stake blocks (DKK 100) compared to control blocks, reflecting the increased motivational relevance of the financial volatility.

- **Feedback Related Negativity (FRN):** A negative-going component peaking between 200–350ms post-feedback, typically localized to the Anterior Cingulate Cortex (ACC). The FRN performs a binary evaluation of outcomes. In this design, we expect the FRN to be most pronounced in Condition B (Loss) and Condition C (FOMO), where the outcome is worse than the counterfactual alternative. The FRN tracks the prediction error of the market shock, signaling a negative deviation from the participant's expected utility.
