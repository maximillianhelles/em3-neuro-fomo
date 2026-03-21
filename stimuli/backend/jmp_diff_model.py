import yaml
import numpy as np
import matplotlib.pyplot as plt
import random
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

def calc_jdm_values(
        init_value=100, drift=params["jdm"]["mu"], 
        volatility=params["jdm"]["sigma"]*2, periods=params["jdm"]["periods"],
        jump=params["jdm"]["jdm"], std_jump=params["jdm"]["sigma_jump"],
        direction=1):
    
    # GBM calculation
    shocks = np.random.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    gbm_values = np.insert(gbm_values, 0, init_value).tolist()

    # Intraday spike
    jump_point = random.randint(int(periods/10), periods - int(periods/10)) # ensures 10% margin for start and end
    value = gbm_values[jump_point]
    pct_jump = np.random.normal(jump, std_jump)
    value *= 1+direction*pct_jump

    # Update GBM values 
    pre_values = gbm_values[:jump_point]
    remaining_shocks = shocks[jump_point:]
    pre_values.append(value)
    post_values = value * np.exp(np.cumsum(remaining_shocks))
    total_values = pre_values + post_values.tolist()

    return total_values, direction*pct_jump, jump_point

# test, jump, jump_point = calc_jdm_values()
# print(f"--- VALUES --- \n {test}")
# print(f"\n --- PERCENTAGE JUMP --- \n {round(jump*100, 2)}%")

# plt.plot(test, label="Asset Price", color='blue')
# plt.ylim(85, 115)
# plt.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
# plt.show()
