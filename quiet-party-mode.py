#!/usr/bin/python
"""

Arrange all speakers into a auiet volume partymode using a speaker
with a queue

"""

# system
import sys

# local
import soco
import requests.packages.urllib3.exceptions


from common import find_all_coordinators


QUIET_VOLUME = 10

def main():
    """Main method"""

    try:
        (speakers, coords) = find_all_coordinators()
        if speakers is None:
            raise Exception("Could not find any speakers")
        if len(coords) == 0:
            raise Exception("Could not find any coordinators in speakers")

        coords_with_queues = [s for s in coords if s.queue_size > 0]

        coord = coords_with_queues[0]

        coord.partymode()

        for s in speakers:
            s.volume = QUIET_VOLUME

        print "Arranged speakers into group: " + coord.group.label

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
        print "Network error: " + str(exc)

    sys.exit(0)


if __name__ == '__main__':
    main()
