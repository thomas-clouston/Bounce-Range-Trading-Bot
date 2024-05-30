# Decisions
def decision(current_position, change, bounce_range, change_period, bounce_continuation):
    close = False
    if current_position == 'buy':
        bounce_range = -abs(bounce_range)

        if change <= (bounce_range * 2):
            close = True
        elif change < 0:
            change_period += change
            bounce_continuation = True
            if change_period < (bounce_range * 2):
                close = True
        elif change >= 0:
            if bounce_continuation is True:
                bounce_continuation = False
            else:
                change_period = 0

    elif current_position == 'sell':
        bounce_range = abs(bounce_range)

        if change >= (bounce_range * 2):
            close = True
        elif change > 0:
            change_period += change
            bounce_continuation = True
            if change_period > (bounce_range * 2):
                close = True
        elif change <= 0:
            if bounce_continuation is True:
                bounce_continuation = False
            else:
                change_period = 0

    return change_period, close, bounce_continuation
