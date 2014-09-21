#!/usr/bin/python
"""
Save the queue as a new sonos playlist

USAGE: sonos-save-queue.py [TITLE]

If no TITLE is given, a title based on the current date is used
like "Saved Queue YYYY-MM-DD"

"""

# system
import logging
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# 2.7+
import argparse

# local
import soco
import requests.packages.urllib3.exceptions

from common import find_all_coordinators, get_queue_size, create_sonos_playlist_from_queue


LOGGER = logging.getLogger('sonos-save-queue')

def main():
    """Main method"""

    parser = argparse.ArgumentParser(description='Inspect SONOS playlist')
    parser.add_argument('-d', '--debug',
                        action = 'store_true',
                        default = False,
                        help = 'debug messages (default: False)')

    parser.add_argument('title', metavar='TITLE', nargs='?',
                        help='new playlist title')
    args = parser.parse_args()

    debug = args.debug
    title = args.title
    ######################################################################

    if debug:
      level = logging.DEBUG
    else:
      level = logging.ERROR
    logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s', 
                        level = level)

    try:
        (speakers, coords) = find_all_coordinators()
        if speakers is None:
            raise "Could not find any speakers"
        if len(coords) == 0:
            raise "Could not find any coordinators in speakers"

        coords_with_queues = [s for s in coords if get_queue_size(s) > 0]

        coord = coords_with_queues[0]

        if title is None:
            import datetime
            now = datetime.date.today()
            title = "Saved Queue {:04d}-{:02d}-{:02d}".format(now.year, 
                                                              now.month,
                                                              now.day)

        print "Saving queue into new playlist '{0}'".format(title)

        playlist = create_sonos_playlist_from_queue(coord, title)

        print "Created sonos playlist {0} - '{1}' ".format(playlist.item_id,
                                                           playlist.title)

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
        print "Network error: " + str(exc)

    sys.exit(0)


if __name__ == '__main__':
    main()
