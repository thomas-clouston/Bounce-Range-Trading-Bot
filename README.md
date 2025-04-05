# Bounce Range Trading Bot

This software currently only supports backtesting functionality for a bot that trades Crypto Perpetual Futures Contracts autonomously on the ByBit exchange. It uses a custom trading stratergy I call Bounce Range Trading where the bot scans the exchange for a coin with the most visible linear trend using linear regression and then further analyses the coin for its average movement against the given linear trend (The Bounce Range), and with this information the bot makes decisions based on current and future price action. 

### Usage

Aquire an api key from the ByBit exchange.

Fill in parameters and run main.py
