import pandas as pd
import statsmodels.tsa.stattools as ts
import seaborn

import numpy as np
import cointegration
import statistics



import matplotlib.pyplot as plt


def get_mean(lst, start, end):
    return sum(lst[start:(end+1)]) / len(lst[start:(end+1)])


def get_stan_dev(lst, start, end):
    return statistics.pstdev(lst[start: (end+1)])


def z_score(val1, val2, lst, start, end):
    ratio = val1 / val2
    return (ratio - get_mean(lst, start, end)) / (get_stan_dev(lst, start, end))


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


def trade_simple(ratio, stock1, stock2, index, start, end):
    cur_score = z_score(stock1[index], stock2[index], ratio, start, end)
    case = 0
    if (cur_score > 1):
        case = 1
    if (cur_score < -1):
        case = 2
    cur_score = max(cur_score, -1 * cur_score)
    return case, cur_score


def testing(train_start, start,ratio, stock1, stock2, model, starting_amount, const): # const should be >=5
    portfolio_value = starting_amount
    stock1_owned = 0
    stock2_owned = 0
    case = 0
    cur_score = 0
    buy_time = []
    buy_price = []
    sell_time = []
    sell_price = []
    for i in range(start, len(ratio)):
        if (model == 1):  # simple
            case, cur_score = trade_simple(ratio, stock1, stock2, i, train_start, start-1)
        else:
            case, cur_score = trade_moving(ratio, stock1, stock2, i)
        if (case == 1):
            sell_time.append(i)
            sell_price.append(stock1[i])

            amount_sold = min(stock1_owned, (portfolio_value * cur_score)/(stock1[i] * const))
            stock1_owned -= amount_sold
            portfolio_value += amount_sold * stock1[i]

            buy_time.append(i)
            buy_price.append(stock2[i])

            amount_bought = min((portfolio_value * cur_score)/(stock2[i] * const), portfolio_value/stock2[i])
            stock2_owned += amount_bought
            portfolio_value -= amount_bought * stock2[i]
        elif (case == 2):
            sell_time.append(i)
            sell_price.append(stock2[i])

            amount_sold = min(stock2_owned, (portfolio_value * cur_score)/(stock2[i] * const))
            stock2_owned -= amount_sold
            portfolio_value += amount_sold * stock2[i]

            buy_time.append(i)
            buy_price.append(stock1[i])

            amount_bought = min((portfolio_value * cur_score)/(stock1[i] * const), portfolio_value/stock1[i])
            stock1_owned += amount_bought
            portfolio_value -= amount_bought * stock1[i]

    portfolio_value += stock1_owned * stock1[len(ratio) - 1] + stock2_owned * stock2[len(ratio) - 1]
    if(model == 1):
        print("Simple Z-Score Model: ")
    else:
        print("Moving Average Z-Score Model: ")
    print("Principal: ", starting_amount)
    print("Final Portfolio Value: ", portfolio_value)
    print("Net Profit: ", (portfolio_value-starting_amount))
    print("Percent Profit: ", ((portfolio_value-starting_amount)/starting_amount))
    print()

    return buy_time, sell_time, buy_price, sell_price

def graphTrends(stock1, stock2, buy_time, sell_time, buy_price, sell_price):
    plt.plot(stock1)
    plt.plot(stock2)
    plt.scatter(buy_time, buy_price, marker=6, color='green')
    plt.scatter(sell_time, sell_price, marker=7, color='red')
    plt.show()

def main():

    start_pointer = 2
    end_pointer = 1393
    stock_series = cointegration.get_data(start_pointer, end_pointer)
    tickers, pairs, p_values, coint_sec = cointegration.perform_coint(start_pointer, end_pointer)

    stock1 = stock_series[pairs[1][0]].tolist()
    stock2 = stock_series[pairs[1][1]].tolist()

    ratio = np.divide(stock_series[pairs[1][0]].tolist(), stock_series[pairs[1][1]].tolist())

    # testing_moving(ratio, stock1, stock2, 1)
    testing(2, 637, ratio, stock1, stock2, 2, 100000, 10)
    testing(2, 637, ratio, stock1, stock2, 1, 100000, 10)


main()