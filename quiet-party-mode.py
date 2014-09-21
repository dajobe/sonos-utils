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


from common import speaker_group_label, short_speaker_group_label, find_all_coordinators, get_queue_size


QUIET_VOLUME = 12

def main():
    """Main method"""

    try:
        (speakers, coords) = find_all_coordinators()
        if speakers is None:
            raise "Could not find any speakers"
        if len(coords) == 0:
            raise "Could not find any coordinators in speakers"

        coords_with_queues = [s for s in coords if get_queue_size(s) > 0]

        coord = coords_with_queues[0]

        coord.partymode()

        for s in speakers:
            s.volume = QUIET_VOLUME

        print "Arranged speakers into group: " + speaker_group_label(coord)

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
        print "Network error: " + str(exc)

    sys.exit(0)


if __name__ == '__main__':
    main()
