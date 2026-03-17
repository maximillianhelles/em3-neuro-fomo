# Experimental Methods 3: Neurological Responses to Controlled Financial Volatility and Counterfactual Regret
For full transparency, this repository contains all files relevant to the author's project in Experimental Methods 3 and contains all necessary files to replicate it as well as the code used for data processing. Additionally, the associated paper and this README will offer insights, discussions, and conclusions in regards to flaws, validity, and future studies.

### Objective
This study's objective is to investigate Event-Related Potentials (ERPs) associated with sudden financial volatility as well as bi-directional counterfactual outcomes (e.g., 'Fear of Missing Out' on gains vs. 'Relief' from avoiding losses). Using a Jump-Diffusion model to simulate stochastic stock movements, we time-lock EEG recordings to discrete market 'shocks,' observing how neural responses scale with real monetary risk and foregone alternatives.

### Experimental Setup & Environment
* **Recording:** A (num-of-electrodes) EEG-headset.
* **Faraday Cage:** Experiments were conducted within the Faraday Cage to minimize external electromagnetic noise.
* **Stimulus Display:** A continuous line chart mimicking the price fluctuations of a fictional financial asset, displayed alongside real-time portfolio values for both the chosen position and its counterfactual alternative. The chart y-axis is fixed ([85:115]) to ensure that GBM noise remains visually subordinate to the experimentally induced volatility spikes.

### The Stimulus
* **Base Action:** The base fluctuations of the asset were determined by Geometric Brownian Motion, using parameters empirically estimated from the S&P-500 index. Visit *stimuli/backend/jmp_diff_model.py* for stimulus implementation, *analysis/pre/gbm_params.py* for parameter estimation logic, and *config/params.yaml* for actual parameters.
* **Spikes:** At randomized points within 10% and 90% of the trial duration, the model introduces sudden volatility in a direction predetermined by condition assignment, mimicking volatility spikes that frequently occur in real markets (e.g. following a company's earnings release).
* **Behavioral Agency:** To induce genuine emotional investment while preserving experimental control, participants were presented with a binary choice between two masked options at the start of each trial — one leading to an invested position and one to a cash position. Participants were unaware of which option corresponded to which position. This design leverages the endowment effect and sense of agency to elicit genuine loss aversion and counterfactual regret, while ensuring full experimental control over condition assignment. Full disclosure of this procedure was provided during post-session debriefing.
* **Real-Time Counterfactual Display:** During each trial, participants could observe both their actual portfolio value and the value of the unchosen alternative updating in real time alongside the chart. This continuous counterfactual exposure was designed to strengthen the affective magnitude of FOMO and relief responses. Portfolio values were displayed in peripheral vision to minimize interference with spike-locked ERP components.
* **Inter-Trial Recovery:** A 10-second fixation cross was presented between successive trials to allow for affective baseline restoration. This interval serves as a washout period, neutralizing the psychological impact of prior market shocks and preventing carryover effects between trials.

### Design & Incentivization
The experiment was divided into three separate blocks:
* **Block 1 - Control:** Participants merely observed the movements of the graph with no capital at stake.
* **Block 2 - DKK 50:** Given 50 DKK capital per trial.
* **Block 3 - DKK 100:** Given 100 DKK capital per trial.

Block order was counterbalanced across participants for blocks 2 and 3. Concluding the experiment, the participant received the initial capital plus any returns of a randomly selected trial from either block two or three. This incentive structure was designed to ensure genuine activation of the brain's mesolimbic pathways. Due to the anticipated low sample size, the experiment was designed as a within-subject design.

### Conditions
In order to measure both actual financial impacts and counterfactual outcomes, conditions follow a 2x2 matrix:
<div align="center">

| | Invested | Not Invested |
| :--- | :---: | :---: |
| **Positive Spike** | Condition A: Gain | Condition C: FOMO |
| **Negative Spike** | Condition B: Loss | Condition D: Relief |

</div>

Spike direction was predetermined by condition assignment. Randomization applied only to spike timing within each trial (between 10% and 90% of trial duration). Conditions were strictly counterbalanced across trials within each block to ensure equal representation.

### Trial Flow
1. **Binary choice** — participant selects one of two masked options, determining their position (invested or cash) for the trial
2. **Position confirmation** — participant is informed of the consequence of their choice
3. **GBM trial** — chart runs with real-time portfolio values displayed for both actual and counterfactual positions; spike occurs at a randomized point
4. **SAM rating** — participant rates current valence and arousal using the Self-Assessment Manikin scale
5. **Fixation cross** — 10-second inter-trial interval

### Neurological Markers
The analysis will focus on the two primary ERPs known to be present in such tasks:
* **The P300 Wave:** A positive-going deflection occurring approximately 300–600ms post-stimulus, primarily distributed over the parietal scalp. In this study, the P300 serves as an index of salience and context updating, expected to scale with the surprise element of the Jump-Diffusion spikes. We hypothesize that P300 amplitudes will be significantly larger in high-stake blocks (DKK 100) compared to control blocks, reflecting the increased motivational relevance of the financial volatility.

* **Feedback Related Negativity (FRN):** A negative-going component peaking between 200–350ms post-feedback, typically localized to the Anterior Cingulate Cortex (ACC). The FRN performs a binary evaluation of outcomes. In this design, we expect the FRN to be most pronounced in Condition B (Loss) and Condition C (FOMO), where the outcome is worse than the counterfactual alternative. The FRN tracks the prediction error of the market shock, signaling a negative deviation from the participant's expected utility.