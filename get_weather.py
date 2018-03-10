"""
Script: get_weather.py

Author: Andrew Toner

Purpose: Go and get all the weather we need and add it to a tweet json file.

Weather is fetched from wunderground https://www.wunderground.com/weather/api/d/docs

Command line parameters

--access_key you-wunderground-access-key
The access key to the wunderground APIs


--nearest_airport Manchester UK/EGCC "New York" US/KJFK Seattle US/KSEA Sydney AU/YSSY
For a name of place, what't the nearest Airport

--average_airport_temp  UK/EGCC 37.6 39.2 42.1 46.6 52.9 57.9 60.4 60.1 56.1 50.2 43.0 39.7
                        AU/YSSY 71.8 71.6 69.6 64.9 59.4 55.0 53.2 55.4 59.4 63.7 66.9 70.2
                        US/KJFK 31.3 32.9 41.0 50.4 59.9 69.3 75.4 74.7 67.5 56.8 47.1 36.5
                        US/KSEA 40.1 43.3 45.5 49.1 55.0 60.8 65.1 65.5 60.4 52.7 45.1 40.5
For an airport, what's the average temperature in a month.

"""

import argparse
from datetime import datetime, timedelta
from time import sleep
import json
import logging
import os
import requests
import sys

weather_cache = {}
average_airport_temps = {}


# Setup Logging
def setup_logger(log_dir=None,
                 log_file=None,
                 log_format=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                 log_level=logging.INFO):
    # Get logger
    logger = logging.getLogger('')
    # Clear logger
    logger.handlers = []
    # Set level
    logger.setLevel(log_level)
    # Setup screen logging (standard out)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(log_format)
    logger.addHandler(sh)
    # Setup file logging
    if log_dir and log_file:
        fh = logging.FileHandler(os.path.join(log_dir, log_file))
        fh.setFormatter(log_format)
        logger.addHandler(fh)

    return logger


def list_json_files():
    """
    :return: A list of all the json files we want to process
    """
    result = []

    for file_name in os.listdir("."):
        if file_name.endswith("_tweets_intent.json"):
            result.append(file_name)

    return result


def test_list_json_files():
    file_list = list_json_files()
    assert isinstance(file_list, list), 'Expected a list'


def create_weather_key(year, month, day, hour, location):
    """
    :return: A consistent hash key based on the year, month, day, hour, and location.
    """
    return '{:4}{:02}{:02}{:02}{}'.format(year, month, day, hour, location)


def test_create_weather_key():
    assert create_weather_key(2018, 1, 29, 20, 'EGCC') == '2018012920EGCC', 'Wrong answer'


def get_wunderground(year, month, day, location):
    """
    Get the wunderground weather for a year, month, year, and location and store it in the cache
    """
    day_string = '{:4d}{:02}{:02}'.format(year, month, day)

    response = requests.get(
        'http://api.wunderground.com/api/' + args.access_key + '/history_' + day_string + '/q/' + location + '.json')

    if response.ok:
        data = json.loads(response.text)

        for observation in data['history']['observations']:
            key = create_weather_key(int(observation['utcdate']['year']), int(observation['utcdate']['mon']),
                                     int(observation['utcdate']['mday']), int(observation['utcdate']['hour']),
                                     location)

            entry = {'temp': float(observation['tempi']), 'humidity': float(observation['hum']),
                     'conditions': observation['conds'],
                     'fog': bool(observation['fog'] == '1'), 'rain': bool(observation['rain'] == '1'),
                     'snow': bool(observation['snow'] == '1'),
                     'hail': bool(observation['hail'] == '1'), 'thunder': bool(observation['thunder'] == 1),
                     'tornado': bool(observation['tornado'] == '1')
                     }

            weather_cache[key] = entry
    else:
        log.error('Failed {}'.format(response))

    # Crappy pause to stop wunderground throttling us.
    sleep(6)


def test_get_wundergroung():
    weather_cache.clear()
    get_wunderground(2018, 1, 21, 'EGCC')
    assert len(weather_cache) != 0, "Weather cache wasn't updated"
    return


def get_weather(year, month, day, hour, location):
    """
    Given the date and location, find the weather from the cache.
    If we can't find it in the cache make the call to grab the weather
    """
    composite_key = create_weather_key(year, month, day, hour, location)

    # If we don't have this, go on line and warm the cache (today, the previous day and tomorrow).
    if composite_key not in weather_cache:
        log.debug('get_weather: cache_miss for {}'.format(composite_key))
        get_wunderground(year, month, day, location)

        # Warm up the cache with the previous day too because wunderground and timezones is funky
        this_day = datetime(year, month, day)

        previous_day = this_day - timedelta(days=1)
        get_wunderground(previous_day.year, previous_day.month, previous_day.day, location)

        next_day = this_day + timedelta(days=1)
        get_wunderground(next_day.year, next_day.month, next_day.day, location)

    else:
        return weather_cache[composite_key]

    # If we don't have it now we're done!
    if composite_key not in weather_cache:
        weather_cache[composite_key] = None

    return weather_cache[composite_key]


def get_average_airport_temp(airport_code, month):
    airport = average_airport_temps[airport_code]
    return airport[month-1]


if __name__ == "__main__":
    # Files and folders
    logging_dir = 'logs'
    time_date = datetime.now()
    string_date = time_date.strftime("%Y%m%d_%H%M%S")

    # Setup Logging
    logging_level = logging.DEBUG
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)
    logging_file = 'get_weather_{}.log'.format(string_date)
    log = setup_logger(logging_dir, logging_file, log_level=logging_level)

    # Grab parameters from the command line
    parser = argparse.ArgumentParser(description='Gets wunderground weather.')
    parser.add_argument('--access_key', type=str, help='wunderground key', required=True)
    parser.add_argument('--nearest_airport', type=str, nargs='*', help='Area to airport code mapping', required=True)
    parser.add_argument('--average_airport_temp', type=str, nargs='*')
    args = parser.parse_args()

    # Grab our airport codes and the city names
    airport_codes = dict(zip(args.nearest_airport[::2], args.nearest_airport[1::2]))

    # Load in the average temps for an airport
    for index in range(0, len(args.average_airport_temp), 13):
        airport_temps = []
        for index_2 in range(index + 1, index + 13):
            airport_temps.append(float(args.average_airport_temp[index_2]))

        average_airport_temps[args.average_airport_temp[index]] = airport_temps

    # Perform unit test --> does not return anything and doesn't accept any arguments!
    test_list_json_files()
    test_create_weather_key()
    test_get_wundergroung()

    # Go through each file at a time
    for file_name in list_json_files():
        output_filename = os.path.splitext(file_name)[0] + '_weather.json'
        file_read = open(file_name, 'r')
        file_write = open(output_filename, 'w')

        # For each tweet we find the weather and append it to the tweet.
        for line in file_read:
            tweet = json.loads(line)

            # Tue Jan 23 03:00:33 +0000 2018
            time = datetime.strptime(tweet['time'], '%a %b %d %H:%M:%S %z %Y')
            location = tweet['location_name']

            airport = airport_codes[location]
            weather = get_weather(time.year, time.month, time.day, time.hour, airport)
            average_weather = {'average_temp': get_average_airport_temp(airport, time.month)}

            if weather is not None:
                tweet.update(weather)

            tweet.update(average_weather)

            file_write.write(json.dumps(tweet) + '\n')

        file_write.close()
        file_read.close()

