""" Common code not yet in SoCo """

# system
import re
import time


import soco

from soco.utils import really_utf8
from soco.xml import XML


def speaker_group_label(speaker):
    """ A description of the group """
    group_names = sorted([m.player_name for m in speaker.group.members])
    return ", ".join(group_names)


def short_speaker_group_label(speaker):
    """ A short description of the group """
    group_names = sorted([m.player_name for m in speaker.group.members])
    group_label = group_names[0]
    if len(group_names) > 1:
        group_label += " + {0}".format(len(group_names)-1)
    return group_label


def find_all_coordinators(attempts=5):
    """ Find all speakers and coordinators """
    coords = []

    for _ in range(0, attempts):
        speakers = soco.discover(timeout=5)
        if speakers is not None:
            break
        time.sleep(1)
    if speakers is not None:
        for speaker in speakers:
            if speaker.is_coordinator:
                coords.append(speaker)
    return (speakers, coords)


def get_all_queue_items(speaker):
    """ get a list of all items in the queue """
    batch_size = 400
    start = 0
    total = None

    playlist_items = []
    while True:
        out = speaker.get_queue(max_items=batch_size, start=start)
        if total is None:
            total = out.total_matches

        playlist_items += out[:]
        start += len(out)
        if start >= total:
            break

    return playlist_items


def is_playing_tv(speaker):
    """ Is the speaker input from TV?

    return True or False
    """
    response = speaker.avTransport.GetPositionInfo([
        ('InstanceID', 0),
        ('Channel', 'Master')
    ])
    track_uri = response['TrackURI']
    return re.match(r'^x-sonos-htastream:', track_uri) is not None


def get_all_playlist_items(speaker, playlist):
    """ get a list of all items in the given playlist """
    batch_size = 400
    start = 0
    total = None

    playlist_items = []
    while True:
        out = speaker.browse(playlist, max_items=batch_size, start=start)
        if total is None:
            total = out.total_matches

        playlist_items += out[:]
        start += len(out)
        if start >= total:
            break

    return playlist_items


from soco.data_structures import MLSonosPlaylist


def create_sonos_playlist_from_queue(speaker, title):
    """ Create a new sonos playlist from the queue.

        :params title: Name of the playlist

        :returns: An instance of
            :py:class:`~.soco.data_structures.MLSonosPlaylist`

    """
    # Note: probably same as Queue service method SaveAsSonosPlaylist
    # but this has not been tested.  This method is what the
    # controller uses.
    response = speaker.avTransport.SaveQueue([
        ('InstanceID', 0),
        ('Title', title),
        ('ObjectID', '')
    ])
    obj_id = response['AssignedObjectID'].split(':', 2)[1]
    uri = "file:///jffs/settings/savedqueues.rsq#{0}".format(obj_id)

    return MLSonosPlaylist(uri, title, 'SQ:')
