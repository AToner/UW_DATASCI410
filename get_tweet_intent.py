"""
Script: get_tweet_intent.py

Author: Andrew Toner

Purpose: Take out json file of scrubbed tweets and call AWS Comprehend to get the intent "tone" of the text

Example command line

--access_key=[AWS Access key]
--secret_access_key=[AWS Secret Access Key]

"""

import argparse
import boto3
import datetime
import json
import logging
import os
import sys


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
    result = []

    for file_name in os.listdir("."):
        if file_name.endswith("_tweets.json"):
            result.append(file_name)

    return result


def test_list_json_files():
    file_list = list_json_files()
    assert isinstance(file_list, list), 'Expected a list'


if __name__ == "__main__":
    # Files and folders
    logging_dir = 'logs'
    time_date = datetime.datetime.now()
    string_date = time_date.strftime("%Y%m%d_%H%M%S")

    # Setup Logging
    logging_level = logging.DEBUG
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)
    logging_file = 'get_tweet_intent_{}.log'.format(string_date)
    log = setup_logger(logging_dir, logging_file, log_level=logging_level)

    # Grab parameters from the command line
    parser = argparse.ArgumentParser(description='Moves all txt files to a S3 bucket.')
    parser.add_argument('--access_key', type=str, help='AWS Access Key', required=True)
    parser.add_argument('--secret_access_key', type=str, help='AWS Secret Access Key', required=True)
    args = parser.parse_args()

    # Perform unit test --> does not return anything and doesn't accept any arguments!
    test_list_json_files()

    comprehend = boto3.client('comprehend', aws_access_key_id=args.access_key,
                              aws_secret_access_key=args.secret_access_key)

    # Loop through all the json tweet files
    for file_name in list_json_files():
        output_filename = os.path.splitext(file_name)[0] + '_intent.json'
        file_read = open(file_name, 'r')
        file_write = open(output_filename, 'w')

        # For each tweet call AWS Comprehend and append the result to the tweet.
        for line in file_read:
            tweet = json.loads(line)

            sentiment_result = comprehend.detect_sentiment(LanguageCode='en', Text=tweet['text'])
            sentiment_score = sentiment_result['SentimentScore']
            flat_sentiment = {'SentimentMixed': sentiment_score['Mixed'],
                              'SentimentNegative': sentiment_score['Negative'],
                              'SentimentNeutral': sentiment_score['Neutral'],
                              'SentimentPositive': sentiment_score['Positive']}

            tweet.update(flat_sentiment)
            file_write.write(json.dumps(tweet) + '\n')

        file_write.close()
        file_read.close()
