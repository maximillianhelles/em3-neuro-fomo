import csv
import matplotlib.pyplot as plt
import random

file_path = "Data/Historical Financial Data/S&P2016-Present.csv"

with open(file_path, "r") as file:
    reader = csv.DictReader(file)
    btc_data = list(reader)

datapoints = len(btc_data)
interval_length = 500
rand_num = random.randint(0, datapoints - interval_length)

sample = btc_data[rand_num : rand_num + interval_length]
dates = [row['\ufeff"Date"'].split()[0] for row in sample][::5]
prices = [float(row['Price'].replace(',', '')) for row in sample][::5]

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