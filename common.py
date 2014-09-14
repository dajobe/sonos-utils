""" Common code not yet in SoCo """

# system
import re
import time


import soco

from soco.utils import really_utf8
from soco.xml import XML


def find_a_coordinator(attempts=5):
    """ Find a coordinator speaker """
    coords = []

    for count in range(0, attempts):
        speakers = soco.discover()
        if speakers is not None:
            break
    time.sleep(1)

    for speaker in speakers:
        if speaker.is_coordinator:
            coords.append(speaker)
    return (speakers, coords)


def get_queue_size(speaker):
    """ Get queue size """

    response = speaker.contentDirectory.Browse([
        ('ObjectID', 'Q:0'),
        ('BrowseFlag', 'BrowseMetadata'),
        ('Filter', '*'),
        ('StartingIndex', 0),
        ('RequestedCount', 0),
        ('SortCriteria', '')
        ])
    result = response['Result']
    if not result:
        return None

    result_dom = XML.fromstring(really_utf8(result))

    container = result_dom.find(\
       '{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}container')

    return int(container.get('childCount'))


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
        out = speaker.browse(playlist, max_items = batch_size, start=start)
        if total is None:
            total = out.total_matches

        playlist_items += out[:]
        start += len(out)
        if start >= total:
            break

    return playlist_items

