import pandas as pd
import statsmodels.tsa.stattools as ts
import seaborn
import csv
import numpy as np
import cointegration
import statistics


import matplotlib.pyplot as plt
def mean(lst):
    return sum(lst) / len(lst)
def stan_dev(lst):
    return statistics.pstdev(lst)
def z_score(val1, val2, lst):
    ratio = val1/val2
    return (ratio - mean(lst))/(stan_dev(lst))

def main():
    start_pointer = 2
    end_pointer = 638
    stock_series = cointegration.get_data(start_pointer, end_pointer)
    tickers, pairs, p_values, coint_sec = cointegration.perform_coint(start_pointer, end_pointer)

    stock1 = stock_series[pairs[1][0]].tolist()
    stock2 = stock_series[pairs[1][1]].tolist()

    ratio =np.divide(stock_series[pairs[1][0]].tolist(),stock_series[pairs[1][1]].tolist())
    print(mean(ratio))
    print(ratio)
    netGains = 0
    stock1_owned = 0
    stock2_owned = 0

    const = 10
    all_z_score = [];
    for i in range(0, len(ratio)):
        all_z_score.append(z_score(stock1[i], stock2[i], ratio))
    print(all_z_score)

    for i in range(0, len(ratio)):
        cur_score = z_score(stock1[i], stock2[i], ratio)
        if (cur_score > 1) :
            stock1_owned -= min(stock1_owned, cur_score*const)
            netGains += cur_score*stock1[i]*const

            stock2_owned += cur_score*const
            netGains-= cur_score*stock2[i]*const
        elif (cur_score < -1):
            stock2_owned -= min(stock2_owned, -1*cur_score * const)
            netGains += -1*cur_score * stock2[i] * const

            stock1_owned += -1*cur_score * const
            netGains -= -1*cur_score * stock1[i] * const
    print(netGains)
    print(stock1_owned)
    print(stock2_owned)
main()