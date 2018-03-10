"""
Script: scrub_twitter_file.py

Author: Andrew Toner

Purpose: Take the raw twitter files, scrub out fields we don't want, and add the name of the location removing the ones
            with no location.

Command line

--boundary -122.459696 47.491912 -122.224433 47.734145
--boundary -74.077185 40.679108 -73.850592 40.839301
--boundary -2.363539 53.399903 -2.123899 53.554376
--boundary 150.919615 -34.001366 151.338469 33.733399
--boundary_name=Seattle
--boundary_name="New York"
--boundary_name=Manchester
--boundary_name=Sydney
"""

import argparse
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


def midpoint(p1, p2):
    """
    Get the midpoint of two values
    """
    return (p1 + p2) / 2


def get_location_name(location=[], boundaries=[], boundary_names=[]):
    """
    Given a location, a list of boundary boxes, and a list of names find the name of the location

    :param location: The location we're checking
    :param boundaries:  The boundary boxes we care about
    :param boundary_names:  The names of the boundary boxes
    :return: The naame of the location
    """
    result = ''

    for index, boundary in enumerate(boundaries):
        long_max = max(boundary[0], boundary[2])
        long_min = min(boundary[0], boundary[2])
        lat_max = max(boundary[1], boundary[3])
        lat_min = min(boundary[1], boundary[3])
        if long_min <= location[0] <= long_max and lat_min <= location[1] <= lat_max:
            result = boundary_names[index]
            break

    return result


def list_txt_files():
    """
    :return: List of all the text files in the current location
    """
    result = []

    for file_name in os.listdir("."):
        if file_name.endswith("_tweets.txt"):
            result.append(file_name)

    return result


def test_get_location_name():
    names = ['Seattle', 'New York', 'Manchester', 'Sydney']
    name = get_location_name([-74.026675, 40.683935],
                             [[-122.459696, 47.491912, -122.224433, 47.734145],
                              [-74.077185, 40.679108, -73.850592, 40.839301],
                              [-2.363539, 53.399903, -2.123899, 53.554376],
                              [150.919615, -34.001366, 151.338469, -33.733399]],
                             names
                             )
    assert name == names[1], 'Should have got New York'


def test_midpoint():
    assert midpoint(1, 3) == 2, 'Wrong answer!'


def test_list_txt_files():
    file_list = list_txt_files()
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
    logging_file = 'scrub_twitter_file_{}.log'.format(string_date)
    log = setup_logger(logging_dir, logging_file, log_level=logging_level)

    # Grab parameters from the command line
    parser = argparse.ArgumentParser(description='Read a lot of tweets into some files.')
    parser.add_argument('--boundary', nargs=4, type=float, action='append', help='Area boundary', required=True)
    parser.add_argument('--boundary_name', nargs=1, type=str, action='append', help='Area boundary', required=True)
    args = parser.parse_args()

    # Create a flattened list of boundary names
    boundary_names = [name for boundary_list in args.boundary_name for name in boundary_list]

    # Perform unit test --> does not return anything and doesn't accept any arguments!
    test_get_location_name()
    test_midpoint()
    test_list_txt_files()

    for file_name in list_txt_files():
        """
        We're going through all our raw tweet files, finding their location, and saving the resulting JSON blob
        If we can't find the location, or it's not within some of our boundaries, we throw the record away.
        """
        output_filename = os.path.splitext(file_name)[0] + '.json'
        file_read = open(file_name, 'r')
        file_write = open(output_filename, 'w')
        total = 0
        used = 0
        for line in file_read:
            total += 1
            tweet = json.loads(line)

            """
            Some tweet API limit has been hit
            """
            if 'limit' in tweet:
                log.info('Hit a limit: {}'.format(tweet))
                break

            """
            Tweet geography comes in two ways.  Either a precise location or within a bounding box.
            We behave slightly differently depending on how we get it.
            """
            if tweet['geo'] is not None:
                # Got a precise location
                location = [tweet['geo']['coordinates'][1], tweet['geo']['coordinates'][0]]
            else:
                # We have a bounding box, so lets find the center
                # Looks like 'coordinates': [[[-8.662663, 49.162656], [-8.662663, 60.86165],
                #                                   [1.768926, 60.86165], [1.768926, 49.162656]]]
                coords = tweet['place']['bounding_box']['coordinates'][0]
                long_1 = coords[0][0]
                long_2 = coords[2][0]
                lat_1 = coords[0][1]
                lat_2 = coords[2][1]
                location = [midpoint(long_1, long_2), midpoint(lat_1, lat_2)]

            # Turn the coordinates into a place name.
            place_name = get_location_name(location, args.boundary, boundary_names)

            # Only use the record if we have place name
            if place_name is not '':
                used += 1
                result = {'id': tweet['id'], 'time': tweet['created_at'], 'location': location,
                          'location_name': place_name,
                          'user_name': tweet['user']['screen_name'], 'text': str.strip(tweet['text'])}
                file_write.write(json.dumps(result) + '\n')

        file_write.close()
        file_read.close()
        log.info(
            '{} - Total records {}.  Records kept {}.  Utilizing {:.2f}%'.format(output_filename, total, used,
                                                                                 (used / total) * 100))
