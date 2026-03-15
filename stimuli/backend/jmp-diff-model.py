import yaml
import numpy as np
import matplotlib.pyplot as plt
import random

params_path = "../../config/params.yaml"

with open(params_path, "r") as f:
    params = yaml.safe_load(f)

def get_prices(
        init_value=params["gbm"]["init_value"], drift=params["gbm"]["mu"], 
        volatility=params["gbm"]["sigma"], periods=params["gbm"]["periods"],
        jump=params["gbm"]["mu_jump"], std_jump=params["gbm"]["sigma_jump"]):
    
    # GBM calculation
    shocks = np.random.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    gbm_values = np.insert(gbm_values, 0, init_value).tolist()

    # Intraday jump
    jump_point = random.randint(int(periods/10), periods - int(periods/10)) # ensures margin for start and end
    value = gbm_values[jump_point]
    pct_jump = np.random.normal(jump, std_jump)
    direction = random.choice([-1,1])
    value *= 1+direction*pct_jump

    # Update GBM values 
    pre_values = gbm_values[:jump_point]
    remaining_shocks = shocks[jump_point+1:]
    pre_values.append(value)
    post_values = value * np.exp(np.cumsum(remaining_shocks))
    total_values = pre_values + post_values.tolist()

    return total_values, pct_jump

test, jump = get_prices()
print(f"--- VALUES --- \n {test}")
print(f"\n --- PERCENTAGE JUMP --- \n {round(jump*100, 2)}%")

plt.plot(test)
#plt.show()