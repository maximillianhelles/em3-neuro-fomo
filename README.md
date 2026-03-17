# Experimental Methods 3: Neurological Responses to Controlled Financial Volatility and Counterfactual Regret
For full transparency, this repository contains all files relevant to the author's project in Experimental Methods 3 and contains all necessary files to replicate it as well as the code used for data processing. Additionally, the associated paper and this README will offer insights, discussions, and conclusions in regards to flaws, validity, and future studies.

### Objective
This study's objective is to investigate Event-Related Potentials (ERPs) associated with sudden financial volatility as well as bi-directional counterfactual outcomes (e.g., 'Fear of Missing Out' on gains vs. 'Relief' from avoiding losses). Using a Jump-Diffusion model to simulate stochastic stock movements, we time-lock EEG recordings to discrete market 'shocks,' observing how neural responses scale with real monetary risk and foregone alternatives.

### Experimental Setup & Environment
* **Recording:** A (num-of-electrodes) EEG-headset.
* **Faraday Cage:** Experiments were conducted within the Faraday Cage to minimize external electromagnetic noise.
* **Stimulus Display:** A continous line chart mimicking the price fluctuations of a fictional financial asset set with a fixed y-axis ([85:115]) ensuring that GBM "noise" remains visually subordinate to the experimental-induced volatility. 

### The Stimulus
* **Base Action:** The base fluctations of the asset was determined by Geometric Brownian Motion, using parameters based on the S&P-500 index. Visit *stimuli/backend/jmp-diff-model.py* for stimuli implementation, *analysis/pre/gbm_params.py* for the logic behind the estimation of parameters, and *config/params.yaml* for actual parameters.
* **Spikes:** At randomized points within 10% and 90% of the trial, the model would introduce sudden volatility in directions determined by conditions to mimic volatility spikes that frequently happen in stock markets (e.g. after a company releases earning).
* **Psychological Ownership:** To induce psychological ownership without introducing agency-related confounds, participants were informed of their position assignment (invested vs. uninvested) prior to each trial via an on-screen prompt. This framing leverages the endowment effect to elicit genuine loss aversion while preserving full experimental control over condition assignment.
* **Inter-trial Recovery:** A 10-second fixation cross was presented between successive trials to allow for affective baseline restoration. This interval serves as a washout period, neutralizing the psychological impact of prior market shocks and preventing any components of the previous trial to carry over to the next trial.

### Design & Incentivization
The experiment were divided into three separate blocks:
* **Block 1 - Control:** Participants merely observed the movements of the graph.
* **Block 2 - DKK 50:** Given 50 DKK capital per trial.
* **Block 3 - DKK 100:** Given 100 DKK capital per trial.

Concluding the experiment, the participant would receive the initial capital plus any returns of a randomly selected trial in either block two or three. This, in addition to psychological ownership, will (hopefully) ensure the activation of the brain's mesolimbic pathways. Due to the low amount of participants, the experiment was designed as a within-subject design.

 ### Conditions
In order to measure both actual financial impacts and counterfactual outcomes, conditions follows a 2x2 matrix:
<div align="center">

| | Invested | Not Invested |
| :--- | :---: | :---: |
| **Positive Spike** | Condition A: Gain | Condition C: FOMO |
| **Negative Spike** | Condition B: Loss | Condition D: Relief |

</div>


### Neurological Markers
The analysis will focus on the two primary ERPs known to be present in such tasks: 
* **The P300 Wave:** A positive-going deflection occurring approximately 300–600ms post-stimulus, primarily distributed over the parietal scalp. In this study, the P300 serves as an index of salience and context updating. It is expected to scale with the "surprise" element of the Jump-Diffusion spikes. We hypothesize that P300 amplitudes will be significantly larger in high-stake blocks (DKK 100) compared to control blocks, reflecting the increased motivational relevance of the financial volatility.

* **Feedback Related Negativity (FRN):** A negative-going component peaking between 200–350ms post-feedback, typically localized to the Anterior Cingulate Cortex (ACC). The FRN performs a "binary evaluation" of outcomes. In this design, we expect the FRN to be most pronounced in Condition B (Loss) and Condition C (FOMO), where the outcome is worse than the counterfactual alternative. The FRN tracks the "prediction error" of the market shock, signaling a negative deviation from the participant's expected utility.
