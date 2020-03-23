import pandas as pd
import statsmodels.tsa.stattools as ts
import seaborn

import numpy as np
import cointegration
import statistics

# to do
# 5 day moving average, more than 1 pair, 100,000


import matplotlib.pyplot as plt


def mean(lst):
    return sum(lst) / len(lst)


def stan_dev(lst):
    return statistics.pstdev(lst)


def z_score(val1, val2, lst):
    ratio = val1 / val2
    return (ratio - mean(lst)) / (stan_dev(lst))


def get_moving_average(ratio_lst, window_size):
    ratio = pd.DataFrame(ratio_lst)
    moving_average = ratio.rolling(window=window_size).mean()
    moving_average_lst = moving_average.values.tolist()
    return moving_average, moving_average_lst


def bollinger_bands(ratio_lst, window_size, num_sd=1):
    ratio = pd.DataFrame(ratio_lst)
    moving_average, moving_average_lst = get_moving_average(ratio_lst, window_size)
    moving_sd = ratio.rolling(window=window_size).std()
    moving_sd_lst = moving_sd.values.tolist()
    upper_band = (moving_average + (moving_sd * num_sd)).values.tolist()
    lower_band = (moving_average - (moving_sd * num_sd)).values.tolist()

    return moving_average_lst, moving_sd_lst, upper_band, lower_band


def moving_z_score(moving_average_short_lst, moving_average_lst, moving_sd_lst, index):
    return (moving_average_short_lst[index][0] - moving_average_lst[index][0]) / (moving_sd_lst[index][0])


def trade_moving(ratio, stock1, stock2, index, window_size=20, short_window_size=5):
    case = 0
    multiplier = 1
    moving_average, moving_sd, upper_band, lower_band = bollinger_bands(ratio, window_size)
    moving_average_short, moving_average_short_lst = get_moving_average(ratio, short_window_size)
    if (moving_average_short_lst[index][0] < lower_band[index][0]):
        case = 2
        multiplier = -1 * moving_z_score(moving_average_short_lst, moving_average, moving_sd, index)
    elif (moving_average_short_lst[index][0] > upper_band[index][0]):
        case = 1
        multiplier = moving_z_score(moving_average_short_lst, moving_average, moving_sd, index)
    return case, multiplier


def trade_simple(ratio, stock1, stock2, index):
    cur_score = z_score(stock1[index], stock2[index], ratio)
    case = 0
    if (cur_score > 1):
        case = 1
    if (cur_score < -1):
        case = 2
    cur_score = max(cur_score, -1 * cur_score)
    return case, cur_score


def testing(ratio, stock1, stock2, model, const):
    netGains = 0
    stock1_owned = 0
    stock2_owned = 0
    case = 0
    cur_score = 0

    for i in range(0, len(ratio)):
        if (model == 1):  # simple
            case, cur_score = trade_simple(ratio, stock1, stock2, i)
        else:
            case, cur_score = trade_moving(ratio, stock1, stock2, i)
        if (case == 1):
            stock1_owned -= min(stock1_owned, cur_score * const)
            netGains += cur_score * stock1[i] * const

            stock2_owned += cur_score * const
            netGains -= cur_score * stock2[i] * const
        elif (case == 2):
            stock2_owned -= min(stock2_owned, cur_score * const)
            netGains += cur_score * stock2[i] * const

            stock1_owned += cur_score * const
            netGains -= cur_score * stock1[i] * const

    # netGains += stock1_owned * stock1[len(ratio) - 1] + stock2_owned * stock2[len(ratio) - 1]

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

    # testing_moving(ratio, stock1, stock2, 1)
    testing(ratio, stock1, stock2, 1, 1)
    testing(ratio, stock1, stock2, 2, 1)


main()