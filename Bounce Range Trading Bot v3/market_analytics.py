# Imports
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
import statistics
import traceback


def analyse_market(minutes, interval, coin_exclude, backtesting, start_time, end_time):
    fail_count = 0

    # Building session
    session = HTTP(
        testnet=False,
        api_key="",
        api_secret="",
    )

    # Analysing market
            for index in pairs:
                trading_pair = index['symbol']
                if trading_pair != coin_exclude:
                    if trading_pair.endswith('USDT'):
                        try:
                            # Pulling candle data
                            if backtesting == True:
                                candle_data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=start_time, end=end_time)
                            else:
                                candle_data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=seconds)

                            candle_data = candle_data['result']['list'][::-1]

                            closing_price = float(candle_data[-1][4])
                            opening_price = float(candle_data[0][1])
                        except:
                            continue
                        candle_data_length = len(candle_data)

                        trend = ((closing_price - opening_price) / opening_price) * 100


                        trends_list.append(abs(trend))
                        trends_list.append(trading_pair)

                        if trend > 0:
                            trend = 'positive'
                        else:
                            trend = 'negative'

                        if backtesting == True:
                            variance = analyse_coin(trading_pair, trend, minutes, interval, clean_threshold, False, backtesting, start_time, end_time)
                            print(variance)
                            if variance > variance_threshold:
                                continue
                        else:
                            variance = analyse_coin(trading_pair, trend, minutes, interval, clean_threshold, False, backtesting, None, None)
                            if variance > variance_threshold:
                                continue

                        gradient = (closing_price - opening_price) / candle_data_length

                        variance_list = []

                        # Calculating predicted values and variance
                        for data in enumerate(candle_data):
                            x = data[0] + 1
                            price = float(data[1][4])
                            y = (gradient * x) + opening_price
                            variance = abs(((price - y) / y) * 100)
                            variance_list.append(variance)

                        average = statistics.mean(variance_list)
                        averages_list.append(average)
                        averages_list.append(trading_pair)

            break

        except Exception:
            fail_count += 1
            if fail_count > 10:
                quit()
            print('Error in Market analytics:', traceback.format_exc())

    fail_count = 0

    # Sorting

    # Sorting trends
    # Define smallest item index value
    for iteration in range(0, len(trends_list), 2):
        smallest = iteration

        # Compares current smallest to rest of array
        for iteration_2 in range(iteration + 2, len(trends_list), 2):

            # Defines new smallest item index value
            if trends_list[iteration_2] < trends_list[smallest]:
                smallest = iteration_2

        # Swap new smallest value with current value
        trends_list[smallest], trends_list[iteration], trends_list[smallest + 1], trends_list[iteration + 1] = trends_list[iteration], trends_list[smallest], trends_list[iteration + 1], trends_list[smallest + 1]

    # Sorting averages
    for iteration in range(0, len(averages_list), 2):
        smallest = iteration

        for iteration_2 in range(iteration + 2, len(averages_list), 2):

            if averages_list[iteration_2] < averages_list[smallest]:
                smallest = iteration_2

        averages_list[smallest], averages_list[iteration], averages_list[smallest + 1], averages_list[iteration + 1] = averages_list[iteration], averages_list[smallest], averages_list[iteration + 1], averages_list[smallest + 1]
    averages_list.reverse()

    # Finding the trading pair's total rank
    for iteration in range(1, len(trends_list), 2):
        trading_pair = trends_list[iteration]
        if trading_pair in averages_list:
            average = averages_list.index(trading_pair)
            index_sum = average + iteration

            # Finding the best pair
            new_pair = [trading_pair, index_sum]
            if len(best_pair) == 0:
                best_pair = new_pair
            elif new_pair[1] > best_pair[1]:
                best_pair = new_pair

    trading_pair = best_pair[0]

    return trading_pair, trend
