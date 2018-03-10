"""
Script: get_twitter_feed.py

Author: Andrew Toner

Purpose: Grab twitter stream for a given set of boundaries.  Output the tweets into files that cover an hour period.

Command line parameters
--boundary -122.459696 47.491912 -122.224433 47.734145
--boundary -74.077185 40.679108 -73.850592 40.839301
--boundary -2.363539 53.399903 -2.123899 53.554376
--boundary 150.919615 -34.001366 151.338469 33.733399
Boundaries that we're interested in from twitter


--consumer_key=[your consumer key]
--consumer_secret=[your consumer secret]
--access_token_key=[your access token key]
--access_token_secret=[your access token secret]
Keys needed by twitter for authentication
"""

import argparse
import datetime
import json
import logging
import os
import sys
import twitter
import types


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


def get_tweet_stream(consumer_key='', consumer_secret='', access_token_key='', access_token_secret='', boundaries=[]):
    """
    Sits and spits out a stream of tweets
    :param consumer_key:
    :param consumer_secret:
    :param access_token_key:
    :param access_token_secret:
    :param boundaries:
    :return: generator of twitter stream
    """
    try:
        api = twitter.Api(consumer_secret=consumer_secret,
                          consumer_key=consumer_key,
                          access_token_key=access_token_key,
                          access_token_secret=access_token_secret)

        stream = api.GetStreamFilter(locations=boundaries)

        for tweets in stream:
            yield json.dumps(tweets)

    except twitter.TwitterError as error:
        log.error('get_tweet_stream: Twitter Error {}'.format(error.message))

    except json.JSONDecodeError as error:
        log.error('get_tweet_stream: JSON Error {}'.format(error.msg))

    except Exception as error:
        log.error('get_tweet_stream: Exception {}'.format(error))

    return


def hour_string():
    date_now = datetime.datetime.now()
    date_string = '{:%Y%m%d%H}'.format(date_now)
    return date_string


def test_hour_string():
    assert len(hour_string()) == 10, 'Expecting 10 digit string'


def test_get_tweet_stream():
    a_stream = get_tweet_stream()

    assert isinstance(a_stream, types.GeneratorType), 'Did not get a generator'


if __name__ == "__main__":
    # Files and folders
    logging_dir = 'logs'
    time_date = datetime.datetime.now()
    string_date = time_date.strftime("%Y%m%d_%H%M%S")

    # Setup Logging
    logging_level = logging.DEBUG
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)
    logging_file = 'get_twitter_feed_{}.log'.format(string_date)
    log = setup_logger(logging_dir, logging_file, log_level=logging_level)

    # Grab parameters from the command line
    parser = argparse.ArgumentParser(description='Read a lot of tweets into some files.')
    parser.add_argument('--consumer_key', type=str, help='Twitter app consumer key', required=True)
    parser.add_argument('--consumer_secret', type=str, help='Twitter app consumer key secret', required=True)
    parser.add_argument('--access_token_key', type=str, help='Twitter app access token key', required=True)
    parser.add_argument('--access_token_secret', type=str, help='Twitter app access token secret', required=True)
    parser.add_argument('--boundary', nargs=4, type=float, action='append', help='Area boundary', required=True)
    args = parser.parse_args()

    flatten_boundaries = [str(coord) for boundary in args.boundary for coord in boundary]

    # Perform unit test --> does not return anything and doesn't accept any arguments!
    test_get_tweet_stream()
    test_hour_string()


    # Open our output file
    current_hour_string = ''
    filename = ''
    output_file = None

    while True:
        """
        We'll sit and read a twitter stream for ever
        """
        tweet_stream = get_tweet_stream(consumer_key=args.consumer_key,
                                        consumer_secret=args.consumer_secret,
                                        access_token_key=args.access_token_key,
                                        access_token_secret=args.access_token_secret,
                                        boundaries=flatten_boundaries)

        try:
            for tweet in tweet_stream:
                # Check to see if we're in a new hour.
                # If so, start a new log file
                if current_hour_string != hour_string():
                    log.info('New hour {}'.format(hour_string()))

                    # Close current file
                    if output_file is not None:
                        log.debug('Closing current output file and renaming')
                        output_file.close()
                        os.rename(filename, filename + '.txt')

                    # Open neq file
                    current_hour_string = hour_string()
                    filename = current_hour_string + '_tweets'
                    log.debug('Creating new output file {}'.format(filename))
                    output_file = open(filename, 'a')

                output_file.write(tweet + '\n')

        except Exception as trouble:
            log.warning('Exception in main loop {}'.format(trouble))
