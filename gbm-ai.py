import random
import matplotlib.pyplot as plt

# --- 24-Hour Simulation Parameters ---
starting_value = 100.0
five_min_volatility = 0.0006 
five_min_drift = 0.00002
periods = 288                

# --- Spike Logic Setup ---
num_spikes = random.choices([0, 1, 2], weights=[0.70, 0.25, 0.05])[0]
spike_intervals = random.sample(range(20, periods - 20), num_spikes)
print(f"Session will have {num_spikes} spike(s) at intervals: {spike_intervals}")

values = [starting_value]

# Initialize the plot
plt.ion()
fig, ax = plt.subplots(figsize=(12, 5))
line, = ax.plot(values, color='#3498db', linewidth=2) 

ax.set_title(f"Intraday Simulation with Variable Earnings Spikes (Total Spikes: {num_spikes})")
ax.set_xlabel("Time (5-Min Increments)")
ax.set_ylabel("Price ($)")
ax.set_xlim(0, periods)

# Start with a standard +/- 2% view
ax.set_ylim(starting_value * 0.98, starting_value * 1.02)
ax.grid(True, linestyle='--', alpha=0.6)

for i in range(periods):
    if i in spike_intervals:
        # Generate the size of the move (Mean: 5%, Std: 2.5%)
        spike_magnitude = random.normalvariate(0.05, 0.025)
        
        # Randomly choose if the news was good (+1) or bad (-1)
        direction = random.choice([1, -1])
        actual_spike_pct = spike_magnitude * direction
        
        starting_value *= (1 + actual_spike_pct)
        
        # Log the spike to the console, but no visual marker is plotted
        print(f"Interval {i} | Spike: {actual_spike_pct * 100:.2f}%")
        
    else:
        # Normal 5-minute movement
        pct_change = random.normalvariate(five_min_drift, five_min_volatility)
        starting_value *= (1 + pct_change)
        
    values.append(starting_value)
    
    # Update plot data
    line.set_ydata(values)
    line.set_xdata(range(len(values)))
    
    # Aggressively update Y-axis limits in case of a massive spike
    current_min, current_max = min(values), max(values)
    if current_min < ax.get_ylim()[0] or current_max > ax.get_ylim()[1]:
        ax.set_ylim(current_min * 0.99, current_max * 1.01)

    plt.pause(0.01) 

plt.ioff()
plt.show()