# Imports
from market_analytics import analyse_market
from coin_analytics import analyse_coin
from position_decider import preform_decision
from kucoin_futures.client import Market, Trade, User
import time


class Run:
    def __init__(self, api_key, api_secret, api_passphrase, fail):
        # Credentials
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

        # Parameters
        self.loss_count = 0
        self.just_opened = False
        self.fail = fail
        self.past_PNL = None
        self.open_position = False
        self.exclude = False

        # Setting up clients

        # Setup trading client
        self.trading_client = Trade(api_key, api_secret, api_passphrase, is_sandbox=False, url='')

        # Setup market client
        self.market_client = Market(url='https://api-futures.kucoin.com')

        # Setup user client
        self.user_client = User(api_key, api_secret, api_passphrase)

        self.main_process()

    # Closing position process
    def closing_process(self, pair):
        count = 0

        while True:
            try:
                close_position = self.trading_client.create_market_order(pair, self.position, '1', closeOrder=True)
                self.open_position = False
                count = 0
                break
            except Exception as e:
                count += 1
                if count > 10:
                    quit()
                print('Error in closing position:', e)

    # Opening position process
    def opening_process(self):
        count = 0

        while True:
            try:
                # Balance
                user = self.user_client.get_account_overview('USDT')
                balance = user['availableBalance']

                # Decide leverage
                if self.close == 'sell':
                    leverage = '1'
                elif self.close == 'buy':
                    leverage = '2'

                # Use quarter of balance
                balance /= 4

                # Lot size
                contract = self.market_client.get_contract_detail(self.trading_pair)
                multiplier = contract['multiplier']

                # Trade amount calculation
                price = self.market_client.get_ticker(self.trading_pair)
                price = price['price']
                price = float("{:.9f}".format(float(price)))

                # Minimum amount
                minimum_amount = price * multiplier

                trade_amount = balance / price
                trade_amount = (trade_amount * int(leverage)) / multiplier

                if trade_amount > minimum_amount:
                    # Preform order
                    open_order = self.trading_client.create_market_order(self.trading_pair, self.close, leverage, size=trade_amount)

                # Checking for order success
                positions = self.trading_client.get_all_position()

                count = 0
                break

            except Exception as e:
                count += 1
                if count > 10:
                    quit()
                print('Error in opening order:', e)

        # If the order failed
        if 'data' in positions:
            self.open_position = False
            self.exclude = False
            self.main_process()

        # If order succeeded
        self.just_opened = True
        self.open_position = True
        self.exclude = False

    # Bot looping
    def main_process(self):
        count = 0

        # Waiting
        time.sleep(60)

        # Finding new coin to trade
        if self.open_position is False:
            if self.exclude is True:
                trade_info = analyse_market(self.coin_exclude)
            else:
                trade_info = analyse_market()

            self.trading_pair = trade_info[0]
            self.position = trade_info[1]

            # Opening new position for new coin
            self.opening_process()

        # Checking PNL
        if self.just_opened is False:
            while True:
                try:
                    PNL = self.trading_client.get_position_details(self.trading_pair)
                    PNL = PNL['unrealisedPnl']

                    count = 0
                    break
                except Exception as e:
                    count += 1
                    if count > 10:
                        quit()
                    print('Error fetching PNL:', e)

            # Checking for unprofitability
            if PNL < 0:
                if self.past_PNL is None:
                    self.past_PNL = PNL

                elif PNL <= self.past_PNL:
                    self.loss_count += 1
                    if self.loss_count == self.fail:
                        self.open_position = False
                        self.loss_count = 0
                        self.past_PNL = None
                        self.exclude = True
                        self.coin_exclude = self.trading_pair
                        self.closing_process(self.trading_pair)
                        self.main_process()

                elif PNL > self.past_PNL:
                    self.past_PNL = PNL
        else:
            self.just_opened = False

        # Evaluating bounce range and making decisions
        while True:
            try:
                issue = 'Error evaluating Bounce range:'

                bounce_range = analyse_coin(self.trading_pair)

                issue = 'Error making decisions:'
                self.close = preform_decision(self.trading_pair, bounce_range)

                count = 0
                break
            except Exception as e:
                count += 1
                if count > 10:
                    quit()
                print(issue, e)

        # If a change in position is needed
        if self.close is True:
            self.closing_process(self.trading_pair)

        # Loop
        self.main_process()
