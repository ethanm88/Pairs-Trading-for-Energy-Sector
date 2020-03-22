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
    ratio = val1 / val2
    return (ratio - mean(lst)) / (stan_dev(lst))


def bollinger_bands(ratio_lst, window_size, num_sd=1):
    ratio = pd.DataFrame(ratio_lst)
    moving_average = ratio.rolling(window=window_size).mean()
    moving_average_lst = moving_average.values.tolist()
    moving_sd = ratio.rolling(window=window_size).std()
    moving_sd_lst = moving_sd.values.tolist()
    upper_band = (moving_average + (moving_sd * num_sd)).values.tolist()
    lower_band = (moving_average - (moving_sd * num_sd)).values.tolist()
    return moving_average_lst, moving_sd_lst, upper_band, lower_band


def moving_z_score(ratio_lst, moving_average_lst, moving_sd_lst, index):
    return (ratio_lst[index] - moving_average_lst[index][0]) / (moving_sd_lst[index][0])


def testing_moving(ratio, stock1, stock2, const):
    netGains = 0
    stock1_owned = 0
    stock2_owned = 0

    window_size = 20
    moving_average, moving_sd, upper_band, lower_band = bollinger_bands(ratio, window_size)

    for i in range(window_size, len(ratio)):
        if (ratio[i] > upper_band[i][0]):
            multiplier = moving_z_score(ratio, moving_average, moving_sd, i)
            stock1_owned -= min(stock1_owned, multiplier * const)
            netGains += multiplier * stock1[i] * const

            stock2_owned += multiplier * const
            netGains -= multiplier * stock2[i] * const
        elif (ratio[i] < lower_band[i][0]):
            multiplier = -1 * moving_z_score(ratio, moving_average, moving_sd, i)
            stock2_owned -= min(stock2_owned, multiplier * const)
            netGains += multiplier * stock2[i] * const

            stock1_owned += multiplier * const
            netGains -= multiplier * stock1[i] * const

    netGains += stock1_owned * stock1[len(ratio) - 1] + stock2_owned * stock2[len(ratio) - 1]

    print(netGains)
    print(stock1_owned)
    print(stock2_owned)


def testing_simple(ratio, stock1, stock2, const):
    netGains = 0
    stock1_owned = 0
    stock2_owned = 0

    for i in range(0, len(ratio)):
        cur_score = z_score(stock1[i], stock2[i], ratio)
        if (cur_score > 1):
            stock1_owned -= min(stock1_owned, cur_score * const)
            netGains += cur_score * stock1[i] * const

            stock2_owned += cur_score * const
            netGains -= cur_score * stock2[i] * const
        elif (cur_score < -1):
            stock2_owned -= min(stock2_owned, -1 * cur_score * const)
            netGains += -1 * cur_score * stock2[i] * const

            stock1_owned += -1 * cur_score * const
            netGains -= -1 * cur_score * stock1[i] * const

    netGains += stock1_owned * stock1[len(ratio) - 1] + stock2_owned * stock2[len(ratio) - 1]

    print(netGains)
    print(stock1_owned)
    print(stock2_owned)


def main():
    start_pointer = 2
    end_pointer = 638
    stock_series = cointegration.get_data(start_pointer, end_pointer)
    tickers, pairs, p_values, coint_sec = cointegration.perform_coint(start_pointer, end_pointer)

    stock1 = stock_series[pairs[1][0]].tolist()
    stock2 = stock_series[pairs[1][1]].tolist()

    ratio = np.divide(stock_series[pairs[1][0]].tolist(), stock_series[pairs[1][1]].tolist())


main()