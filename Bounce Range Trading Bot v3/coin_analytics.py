# Imports
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks
import statistics
import traceback


def analyse_coin(trading_pair, trend, minutes, interval, clean_threshold, position_active, backtesting, start_time, end_time):
    fail_count = 0
    try:
        # Building session
        session = HTTP(
            testnet=False,
            api_key="",
            api_secret="",
        )

        # Finding start time
        current_date = datetime.today() - timedelta(minutes=minutes)
        current_date = current_date.strftime("%d.%m.%Y %H:%M:%S")
        current_date = datetime.strptime(current_date, '%d.%m.%Y %H:%M:%S')
        seconds = int(current_date.timestamp() * 1000)  # Converting week to milliseconds

        if backtesting == True:
            data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=start_time, end=end_time)
        else:
            data = session.get_kline(category="linear", symbol=trading_pair, interval=interval, start=seconds)
        data = data['result']['list'][::-1]

        x_array = []
        y_array = []
        x_count = 0

        # Preparing data
        for iteration in data:
            price = float(iteration[4])
            x_count += 1

            x_array.append(x_count)
            y_array.append(price)

        x = np.array(x_array)
        y = np.array(y_array)  # Reverse numpy array
        if len(y) < 25:
            if position_active == True:
                return None, None
            else:
                return None

        # Apply Savitzky-Golay filter for smoothing
        y_smooth = savgol_filter(y, window_length=25, polyorder=8)

        # Find peaks and troughs
        peaks, properties = find_peaks(y_smooth, distance = 10)
        troughs, properties_t = find_peaks(-y_smooth, distance = 10) # Find troughs by inverting the signal
        '''
        # Plotting the results

        # Frame size
        plt.figure(figsize=(10, 6))

        # Original data
        plt.plot(x, y, label='Original Data', alpha=0.5, color='gray')

        # Smoothed data
        plt.plot(x, y_smooth, label='Smoothed Data', color='blue', linewidth=2)

        # Peaks and Troughs
        plt.scatter(x[peaks], y_smooth[peaks], color='red', label='Peaks', zorder=5)
        plt.scatter(x[troughs], y_smooth[troughs], color='green', label='Troughs', zorder=5)

        # Labels and legend
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Smoothing with Savitzky-Golay Filter and Peak Detection')
        plt.legend()

        # Show the plot
        plt.show()
        '''

        peak_x_values = x[peaks]
        peak_y_values = y_smooth[peaks]
        trough_x_values = x[troughs]
        trough_y_values = y_smooth[troughs]
        temp_bounce_range_values = []

        # Finding bounce ranges

        if trend == 'positive':
            try:
                # Starting with peak to trough
                if peak_x_values[0] > trough_x_values[0]:
                    trough_y_values = np.delete(trough_y_values, 0)
                    trough_x_values = np.delete(trough_x_values, 0)

                # Finding clear peak to trough ranges

                for iteration in range(len(peak_x_values) - 1):
                    peak_x_value = peak_x_values[iteration]
                    peak_y_value = peak_y_values[iteration]
                    count = 1
                    next_peak_x_value = peak_x_values[iteration + count]
                    calculated = False
                    iteration_2 = 0

                    while iteration_2 < len(trough_x_values):
                        trough_x_value = trough_x_values[iteration_2]
                        trough_y_value = trough_y_values[iteration_2]

                        if trough_x_value > peak_x_value:
                            if trough_y_value < peak_y_value:
                                if trough_x_value < next_peak_x_value:
                                    percentage_change = ((trough_y_value - peak_y_value) / peak_y_value) * 100
                                    calculated = True
                                    iteration_2 += 1
                                else:
                                    if calculated == False:
                                        count += 1
                                        try:
                                            next_peak_x_value = peak_x_values[iteration + count]
                                        except:
                                            break
                                        iteration_2 = 0
                                    else:
                                        temp_bounce_range_values.append(abs(percentage_change))
                                        break
                            else:
                                if calculated == True:
                                    temp_bounce_range_values.append(abs(percentage_change))
                                    break
                                else:
                                    iteration_2 += 1
                        else:
                            iteration_2 += 1
            except:
                if position_active == True:
                    return None, None
                else:
                    return None


        elif trend == 'negative':
            try:
                # Starting with trough to peak
                if trough_x_values[0] > peak_x_values[0]:
                    peak_y_values = np.delete(peak_y_values, 0)
                    peak_x_values = np.delete(peak_x_values, 0)

                # Finding clear trough to peak ranges

                for iteration in range(len(trough_x_values) - 1):
                    trough_x_value = trough_x_values[iteration]
                    trough_y_value = trough_y_values[iteration]
                    count = 1
                    next_trough_x_value = trough_x_values[iteration + count]
                    calculated = False
                    iteration_2 = 0

                    while iteration_2 < len(peak_x_values):
                        peak_x_value = peak_x_values[iteration_2]
                        peak_y_value = peak_y_values[iteration_2]

                        if peak_x_value > trough_x_value:
                            if peak_y_value > trough_y_value:
                                if peak_x_value < next_trough_x_value:
                                    percentage_change = ((peak_y_value - trough_y_value) / trough_y_value) * 100
                                    calculated = True
                                    iteration_2 += 1

                                else:
                                    if calculated == False:
                                        count += 1
                                        try:
                                            next_trough_x_value = trough_x_values[iteration + count]
                                        except:
                                            break
                                        iteration_2 = 0
                                    else:
                                        temp_bounce_range_values.append(abs(percentage_change))
                                        break

                            else:
                                if calculated == True:
                                    temp_bounce_range_values.append(abs(percentage_change))
                                    break
                                else:
                                    iteration_2 += 1

                        else:
                            iteration_2 += 1
            except:
                if position_active == True:
                    return None, None
                else:
                    return None


        # Calculating bounce range average
        if len(temp_bounce_range_values) != 0:
            average_bounce_range = statistics.mean(temp_bounce_range_values)
        else:
            average_bounce_range = 0

        bounce_range_values = []

        # Cleaning small irrelevant bounce values
        for iteration in range(len(temp_bounce_range_values)):
            bounce_value = temp_bounce_range_values[iteration]
            equivalence = (bounce_value / average_bounce_range) * 100
            if equivalence > clean_threshold:
                bounce_range_values.append(bounce_value)

        if len(bounce_range_values) != 0:
            average_bounce_range = statistics.mean(bounce_range_values)
        else:
            average_bounce_range = 0

        bounce_range_variance_values = []

        # Finding bounce range differences
        for bounce_value in bounce_range_values:
            bounce_range_variance = abs(((bounce_value - average_bounce_range) / average_bounce_range) * 100)
            bounce_range_variance_values.append(bounce_range_variance)

        # Calculating bounce range difference average
        if len(bounce_range_variance_values) != 0:
            average_bounce_variance = statistics.mean(bounce_range_variance_values)
        else:
            average_bounce_variance = 0

        if position_active == True:
            if trend == 'positive':
                recent_y_value = peak_y_values[-1]
                recent_price = float(data[-1][4])
                percentage_change = ((recent_price - recent_y_value) / recent_y_value) * 100

                return average_bounce_range, percentage_change

            elif trend == 'negative':
                recent_y_value = trough_y_values[-1]
                recent_price = float(data[-1][4])
                percentage_change = ((recent_price - recent_y_value) / recent_y_value) * 100

                return average_bounce_range, percentage_change
        else:
            return average_bounce_variance

    except Exception:
        fail_count += 1
        if fail_count > 10:
            quit()
        print('Error in Market analytics:', traceback.format_exc())


#print(analyse_coin('A8USDT', 'negative', 10080, 60, 30, True, False, None, None))