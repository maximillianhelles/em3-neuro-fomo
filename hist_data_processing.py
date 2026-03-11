import csv
import matplotlib.pyplot as plt
import random

def picker(data, interval_length=500):
    rand_num = random.randint(0, len(data) - interval_length)

    sample = data[rand_num : rand_num + interval_length]
    dates = list(range(len(sample)))[::5]
    prices = [float(sample[row]['Price'].replace(',', '')) for row in range(len(sample))][::-1][::5]

    x_1, x_2 = dates[0], dates[-1]
    y_1, y_2 = prices[0], prices[-1]
    slope = (x_2-x_1)/(y_2-y_1)
    
    return dates, prices, slope

file_path = "Data/Historical Financial Data/S&P2016-Present.csv"

with open(file_path, "r") as file:
    reader = csv.DictReader(file)
    financial_data = list(reader)

dates, prices, slope = picker(financial_data)

change = (prices[-1]-prices[0])/prices[0]
print(f"Change = {int(change*100)}%")

plt.ion()
fig, ax = plt.subplots()

line, = ax.plot([], [], color='orange', linewidth=2)

ax.set_xlim(0, len(prices))
ax.set_ylim(min(prices) * 0.95, max(prices) * 1.05)

ax.set_xticks([])

x, y = [], []

for i in range(len(prices)):
    x.append(i)
    y.append(prices[i])

    line.set_data(x, y)

    plt.pause(0.05)

plt.ioff()
plt.show()