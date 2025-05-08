import time
from market_analytics import analyse_market
from coin_analytics import analyse_coin
from pybit.unified_trading import HTTP
import datetime
import traceback


# Parameters
minutes = 10080
interval = 60
clean_threshold = 30
variance_threshold = 50
bounce_range_threshold = 3
backtesting = True


# Building session
session = HTTP(
        testnet=False,
        api_key="",
        api_secret="",
    )


def add_week_and_shift(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000.0

    # Get the UTC timezone
    utc_timezone = datetime.timezone.utc

    # Convert the timestamp to a timezone-aware datetime object
    original_time = datetime.datetime.fromtimestamp(timestamp_s, utc_timezone)

    # Add 1 week to the time
    week_later_time = original_time + datetime.timedelta(weeks=1)

    # Shift the time forward by the specified number of hours
    shifted_time = week_later_time + datetime.timedelta(hours=1)
    print(f"Shifted time: {shifted_time}")

    # Convert the original time by shifting it by the shift_hours
    original_shifted_time = original_time + datetime.timedelta(hours=1)
    print(f"Current time: {original_shifted_time}")

    # Convert both times back to milliseconds
    original_shifted_timestamp_ms = int(original_shifted_time.timestamp() * 1000)
    shifted_timestamp_ms = int(shifted_time.timestamp() * 1000)

    return original_shifted_timestamp_ms, shifted_timestamp_ms


def open_position(trading_pair, position, start_seconds, end_seconds):
    try:
        if start_seconds and end_seconds != None:
            candle_data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=start_seconds, end=end_seconds)
            candle_data = candle_data['result']['list'][::-1]
            opened_price = float(candle_data[-1][4])
            print(f'Opened {trading_pair} with position {position} at {opened_price}')

            return True, opened_price
        else:
            print(f'Opened {trading_pair} with position {position}')
            return True
    except Exception:
        print('Error opening position:', traceback.format_exc())


def close_position(trading_pair, position):
    print(f'Closed {trading_pair} with position {position}')
    time.sleep(10)  # Backtesting purpose
    return False


def get_pnl(trading_pair, position, start_seconds, end_seconds, opened_price):
    try:
        # Building session
        candle_data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=start_seconds, end=end_seconds)
        candle_data = candle_data['result']['list'][::-1]
        current_price = float(candle_data[-1][4])
        print(f'Current price: {current_price}')

        if position == 'Buy':
            pnl = ((current_price - opened_price) / opened_price)
        elif position == 'Sell':
            pnl = ((opened_price - current_price) / opened_price)

        return pnl
    except Exception:
        print('Error getting pnl:', traceback.format_exc())


def process():
    opened_position = False
    last_traded_trading_pair = None
    opened_price = None  # Backtesting purpose
    backtesting_start_time = 1722434400000  # Backtesting purpose
    bankroll = 1000  # Backtesting purpose

    while True:
        #time.sleep(3600)
        backtesting_start_time, backtesting_end_time = add_week_and_shift(backtesting_start_time)  # Backtesting start time
        if opened_position == False:
            if backtesting == True:
                market_analytics = analyse_market(minutes, interval, last_traded_trading_pair, backtesting, backtesting_start_time, backtesting_end_time, variance_threshold, clean_threshold)
            else:
                market_analytics = analyse_market(minutes, interval, last_traded_trading_pair, backtesting, None, None, variance_threshold, clean_threshold)
            trading_pair = market_analytics[0]
            print(f'Trading pair: {trading_pair}')
            trend = market_analytics[1]
            if trend == 'positive':
                position = 'Buy'
            elif trend == 'negative':
                position = 'Sell'

            if backtesting is True:
                opened_position, opened_price = open_position(trading_pair, position, backtesting_start_time, backtesting_end_time)
            else:
                opened_position = open_position(trading_pair, position, None, None)

            last_traded_trading_pair = trading_pair


        else:
            if backtesting == True:
                coin_analytics = analyse_coin(trading_pair, trend, minutes, interval, clean_threshold, True, backtesting, backtesting_start_time, backtesting_end_time)
            else:
                coin_analytics = analyse_coin(trading_pair, trend, minutes, interval, clean_threshold, True, backtesting, None, None)
            bounce_range = coin_analytics[0]
            percentage_change = coin_analytics[1]

            pnl = get_pnl(trading_pair, position, backtesting_start_time, backtesting_end_time, opened_price)  # Backtesting purpose
            print(f'PNL: {pnl}')

            if bounce_range == None:
                if position == 'Buy':
                    opened_position = close_position(trading_pair, 'Sell')
                    bankroll += (pnl * bankroll)
                elif position == 'Sell':
                    opened_position = close_position(trading_pair, 'Buy')
                    bankroll += (pnl * bankroll)

            else:
                if position == 'Buy':
                    if percentage_change < 0 and abs(percentage_change) > (bounce_range * bounce_range_threshold):
                        opened_position = close_position(trading_pair, 'Sell')
                        bankroll += (pnl * bankroll)
                elif position == 'Sell':
                    if percentage_change > 0 and abs(percentage_change) > (bounce_range * bounce_range_threshold):
                        opened_position = close_position(trading_pair, 'Buy')
                        bankroll += (pnl * bankroll)

        print(f'Bankroll: {bankroll}')

process()
