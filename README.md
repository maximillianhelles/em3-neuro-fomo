# Experimental Methods 3: Neurological Responses to Controlled Financial Volatility and Counterfactual Regret
For full transparency, this repository contains all files relevant to the author's project in Experimental Methods 3 and contains all necessary files to replicate it as well as the code used for data processing. Additionally, the associated paper and this README will offer insights, discussions, and conclusions in regards to flaws, validity, and future studies.

### Objective
This study's objective is to investigate Event-Related Potentials (ERPs) associated with sudden financial volatility as well as bi-directional counterfactual outcomes (e.g., 'Fear of Missing Out' on gains vs. 'Relief' from avoiding losses). Using a Jump-Diffusion model to simulate stochastic stock movements, we time-lock EEG recordings to discrete market 'shocks,' observing how neural responses scale with real monetary risk and foregone alternatives.

### Experimental Setup & Environment
* **Recording:** A (num-of-electrodes) EEG-headset.
* **Faraday Cage:** Experiments were conducted within the Faraday Cage to minimize external electromagnetic noise.
* **Stimulus Display:** A continous line chart mimicking the price fluctuations of a fictional financial asset. 

### The Stimulus
* **Base Action:** The base fluctations of the asset was determined by Geometric Brownian Motion, using parameters based on the S&P-500 index. Visit *stimuli/backend/jmp-diff-model.py* for stimuli implementation, *analysis/pre/gbm_params.py* for the logic behind the estimation of parameters, and *config/params.yaml* for actual parameters.
* **Spikes:** At randomized points within 10% and 90% of the trial, the model would introduce sudden volatility in randomized directions to mimic volatility spikes that frequently happen in stock markets (e.g. after a company releases earning).
* **Behavioral Agency:** To ensure participants felt agency and were psychologically invested in the continously moving price of the asset, the participants were allowed at certain points within the simulated trading session to buy or sell their entire position. This way, participants will (hopefully) view profits / losses as a direct result of their decisions rather than a passive observation.
* **Inter-trial Recovery:** A 10-second fixation cross was presented between successive trials to allow for affective baseline restoration. This interval serves as a washout period, neutralizing the psychological impact of prior market shocks and preventing any components of the previous trial to carry over to the next trial.

### Design & Incentivization
The experiment were divided into three seperate blocks:
* **Block 1 - Control:** Participants merely observed the movements of the graph.
* **Block 2 - DKK 50:** Given 50 DKK capital pr. trial.
* **Block 3 - DKK 100:** Given 100 DKK capital pr. trial.

Concluding the experiment, the participant would receive the initial capital plus any returns of a randomly selected trial in either block two or three. This, in addition to behavioral agency, will (hopefully) ensure the activation of the brain's mesolimbic pathaways. Due to the low amount of participants, the experiment was designed as a within-subject design. 
