# Imports
from kucoin_futures.client import Market
from datetime import datetime, timedelta
import statistics


def analyse_coin(trading_pair):
    # Parameters
    bounce_continuation = False
    trend_interval = 1440
    candle_interval = 15

    # Setup market client
    market_client = Market(url='https://api-futures.kucoin.com')

    # Lists
    bounce_list = []
    temp_candle_list = []

    # Converting week to milliseconds
    current_date = datetime.today() - timedelta(minutes=trend_interval)
    current_date = current_date.strftime("%d.%m.%Y %H:%M:%S")
    current_date = datetime.strptime(current_date, '%d.%m.%Y %H:%M:%S')
    seconds = int(current_date.timestamp() * 1000)

    candle_data = market_client.get_kline_data(trading_pair, candle_interval, seconds)

    opening_trend_price = candle_data[0][1]
    closing_trend_price = candle_data[-1][4]

    # Calculate trend percentages
    trend_change = ((closing_trend_price - opening_trend_price) / opening_trend_price) * 100

    # Finding trends
    if trend_change > 0:
        trend = 'positive'

    else:
        trend = 'negative'

    # Finding all candles times in trend interval
    for iteration in candle_data:
        open_price = iteration[1]
        close_price = iteration[4]

        # Calculate candle percentages
        candle_change = ((close_price - open_price) / open_price) * 100

        # Build list of candles against trend
        if trend == 'positive':
            if candle_change < 0:
                bounce_continuation = True

                if len(temp_candle_list) == 0:
                    temp_candle_list = [candle_change]

                elif temp_candle_list[-1] < 0:  # If the last percent was also negative
                    temp_candle_list.append(candle_change)

            elif candle_change >= 0:
                if len(temp_candle_list) != 0:
                    if bounce_continuation is True:
                        bounce_continuation = False
                    else:
                        temp_candle_list = [abs(number) for number in temp_candle_list]
                        bounce_list.append(sum(temp_candle_list))
                        temp_candle_list = []

        elif trend == 'negative':
            if candle_change > 0:
                bounce_continuation = True

                if len(temp_candle_list) == 0:
                    temp_candle_list = [candle_change]

                elif temp_candle_list[-1] > 0:
                    temp_candle_list.append(candle_change)

            elif candle_change <= 0:
                if len(temp_candle_list) != 0:
                    if bounce_continuation is True:
                        bounce_continuation = False
                    else:
                        bounce_list.append(sum(temp_candle_list))
                        temp_candle_list = []

    # Adding leftovers to bounce list
    if len(temp_candle_list) != 0:

        temp_candle_list = [abs(number) for number in temp_candle_list]
        bounce_list.append(sum(temp_candle_list))

    # Calculating averages
    if len(bounce_list) != 0:
        bounce_range = statistics.mean(bounce_list)
    else:
        bounce_range = 0

    return bounce_range
