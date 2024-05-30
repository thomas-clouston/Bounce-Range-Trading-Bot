# Imports
from coin_decisions import decision
from kucoin_futures.client import Market
from datetime import datetime, timedelta


def preform_decision(trading_pair, bounce_range):
    # Parameters
    change_period = 0
    bounce_continuation = False
    trend_interval = 1440
    candle_interval = 15

    # Setting up client
    market_client = Market(url='https://api-futures.kucoin.com')

    # Fetching data

    current_date = datetime.today() - timedelta(minutes=trend_interval)
    current_date = current_date.strftime("%d.%m.%Y %H:%M:%S")
    current_date = datetime.strptime(current_date, '%d.%m.%Y %H:%M:%S')
    seconds = int(current_date.timestamp() * 1000)

    candle_data = market_client.get_kline_data(trading_pair, candle_interval, seconds)

    opening_price = candle_data[0][1]
    closing_price = candle_data[0][4]
    change = ((closing_price - opening_price) / opening_price) * 100

    if change > 0:
        current_position = 'buy'
    elif change <= 0:
        current_position = 'sell'

    # Simulate position change
    for data in candle_data:

        # Setting price data
        open_price = data[1]
        close_price = data[4]

        # Calculate percentage
        change = ((close_price - open_price) / open_price) * 100

        # Simulate decision
        decisions = decision(current_position, change, bounce_range, change_period, bounce_continuation)
        change_period = decisions[0]
        close = decisions[1]
        bounce_continuation = decisions[2]

    return close
