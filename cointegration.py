#https://machinelearningmastery.com/time-series-data-stationary-python/
#Engle-Grange
import pandas as pd
import statsmodels.tsa.stattools as ts
import seaborn
import csv

import matplotlib.pyplot as plt

#these are line numbers of the csv


def get_data(start_pointer, end_pointer):
    #start_pointer = 2
    #end_pointer = 638
    MAX_INDEX = 4697

    relevant = [*range(start_pointer-2, end_pointer-1, 1)] # isolates section of csv that is relevant
    delete_lower_bound = [*range(0, start_pointer-2, 1)]
    delete_upper_bound = [*range(end_pointer-1, MAX_INDEX-1, 1)]
    to_delete = delete_lower_bound + delete_upper_bound
    stock_series = pd.read_csv('Stock Time.csv')
    stock_series = stock_series.drop(stock_series.index[to_delete])
    return stock_series

def perform_coint(start_pointer, end_pointer):
    stock_series = get_data(start_pointer, end_pointer)
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

    pair_header = ['Stock 1', 'Stock 2']
    pairs = []
    pairs.append(pair_header)

    for i in range(0, len(tickers)):
        for j in range(0, len(tickers)):
            if (i < j) :
                if (p_values[i][j] < threshold):
                    coint_sec[i][j] = 1
                    pairs.append([tickers[i], tickers[j]])
                else:
                    coint_sec[i][j] = 0
            else :
                p_values[i][j] = 0
    return tickers, pairs, p_values, coint_sec

def get_heatmap():
    tickers, pairs, p_values, coint_sec = perform_coint()
    seaborn.heatmap(p_values, xticklabels=tickers,yticklabels=tickers, cmap='RdYlGn_r')
    seaborn.heatmap(coint_sec, xticklabels=tickers,yticklabels=tickers, cmap='RdYlGn_r')
    plt.show()


def write_to_csv():
    tickers, pairs, p_values, coint_sec = perform_coint()
    with open('pairs.csv', mode='w', newline='') as pairs_file:
        pairs_writer = csv.writer(pairs_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(0, len(pairs)):
            pairs_writer.writerow(pairs[i])


