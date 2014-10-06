""" Common code not yet in SoCo """

# system
import re
import time
import urllib


import soco

from soco.utils import really_utf8
from soco.xml import XML
from soco.data_structures import get_ml_item, SearchResult


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


def _escape_path(path):
    return urllib.quote(path.encode('utf-8')).replace('/', '%2F')

def search_track(speaker, artist, album=None, track=None,
                 start=0, max_items=100, full_album_art_uri=False):
    """Search for an artist, artist's albums, or specific track.

    Keyword arguments:
        artist: Artist name
        albumn: Album name
        track: Track name
        start (int): The starting index of the results
        max_items (int): The maximum number of items to return
        full_album_art_uri(bool): If the album art URI should include the
            IP address

    Returns:
        dict: A :py:class:`~.soco.data_structures.SearchResult` object

    Raises:
        SoCoUPnPException: With ``error_code='701'`` if the item cannot be
            found
    """
    search = u'A:ALBUMARTIST/' + _escape_path(artist)
    if album is not None:
        search += u'/' + _escape_path(album)
        if track is not None:
            search += u'/' + _escape_path(track)

    response, metadata = speaker._music_lib_search(search, start, max_items)

    metadata['search_type'] = 'browse'

    # Parse the results
    dom = XML.fromstring(really_utf8(response['Result']))
    item_list = []
    for container in dom:
        item = get_ml_item(container)
        # Check if the album art URI should be fully qualified
        if full_album_art_uri:
            speaker._update_album_art_to_full_uri(item)
        item_list.append(item)

    # pylint: disable=star-args
    return SearchResult(item_list, **metadata)
