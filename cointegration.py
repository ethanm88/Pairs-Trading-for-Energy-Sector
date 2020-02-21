#https://machinelearningmastery.com/time-series-data-stationary-python/
#Engle-Grange
import pandas as pd

import matplotlib.pyplot as plt
data = []
time = []
stock_series = pd.read_csv('Stock Time.csv')

'''
for i in stock_series.columns:
    #print(series[i])
    if i == 1:
        time.append(stock_series[i])
    else:
        data.append(stock_series[i])
'''

print(stock_series['Date'])
x = stock_series['Date']
y = stock_series['XOM']
plt.plot(x,y, 'g-')

axes = plt.gca()

plt.show()


