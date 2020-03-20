#https://machinelearningmastery.com/time-series-data-stationary-python/
#Engle-Grange
import pandas as pd
import statsmodels.tsa.stattools as ts
import seaborn


import matplotlib.pyplot as plt
data = []
time = []
stock_series = pd.read_csv('Stock Time.csv')

p_values = []
coint_sec = []

tickers = ['XOM', 'RDS.A', 'CVX', 'TOT', 'BP', 'PTR', 'SNP', 'SLB', 'EPD', 'E', 'COP', 'EQNR', 'EOG', 'PBR', 'CEO', 'SU', 'OXY', 'HAL']
for i in range(len(tickers)):
    p_values.append([0] * len(tickers))
    coint_sec.append([0] * len(tickers))

for i in range(0, len(tickers)):
    for j in range(0, len(tickers)):
        if (i < j) :
            p_values[i][j] = (ts.coint(stock_series[tickers[i]], stock_series[tickers[j]]))[1]
        else :
            p_values[i][j] = 0.5

threshold = 0.005

for i in range(0, len(tickers)):
    for j in range(0, len(tickers)):
        if (i < j) :
            if (p_values[i][j] < threshold):
                coint_sec[i][j] = 1
            else:
                coint_sec[i][j] = 0
        else :
            p_values[i][j] = 0

seaborn.heatmap(p_values, xticklabels=tickers,yticklabels=tickers, cmap='RdYlGn_r')
seaborn.heatmap(coint_sec, xticklabels=tickers,yticklabels=tickers, cmap='RdYlGn_r')

plt.show()


