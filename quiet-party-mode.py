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


QUIET_VOLUME = 12

def speaker_group_label(speaker):
    """ Get a description of the group a speaker is in """
    group_names = sorted([m.player_name for m in speaker.group.members])
    return ", ".join(group_names)


def short_speaker_group_label(speaker):
    """ Get a short description of the group a speaker is in """
    group_names = sorted([m.player_name for m in speaker.group.members])
    group_label = group_names[0]
    if len(group_names) > 1:
        group_label += " + %d" % (len(group_names)-1, )
    return group_label


def main():
    """Main method"""

    try:
        speakers = soco.discover()

        speakers_with_queues = [s for s in speakers
                                if len(s.get_queue(max_items=1)) > 0]

        coordinators = [s for s in speakers_with_queues if s.is_coordinator]

        coord = coordinators[0]

        coord.partymode()

        for s in speakers:
            s.volume = QUIET_VOLUME

        print "Arranged speakers into group: " + speaker_group_label(coord)

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
        print "Network error: %s" % (str(exc), )

    sys.exit(0)


if __name__ == '__main__':
    main()
