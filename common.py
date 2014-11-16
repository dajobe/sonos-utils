""" Common code not yet in SoCo """

# system
import re
import time
import urllib


import soco

from soco.utils import really_utf8
from soco.xml import XML
from soco.data_structures import get_didl_object, SearchResult


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


def _escape_path(path):
    return urllib.quote(path.encode('utf-8')).replace('/', '%2F')


def search_track(speaker, artist, album=None, track=None,
                 start=0, max_items=100, full_album_art_uri=False):
    """Search for an artist, artist's albums, or specific track.

    Keyword arguments:
        artist: Artist name
        album: Album name
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

    response, metadata = speaker._music_lib_search(search, start, max_items)

    metadata['search_type'] = 'browse'

    # Parse the results
    dom = XML.fromstring(really_utf8(response['Result']))
    item_list = []
    for container in dom:
        item = get_didl_object(container)
        # this does not work: item is MLCategory or item is MLSameArtist
        if item.item_class == 'object.container' or item.item_class == 'object.container.playlistContainer.sameArtist':
            continue

        if track is not None and item.title != track:
            continue

        # Check if the album art URI should be fully qualified
        if full_album_art_uri:
            speaker._update_album_art_to_full_uri(item)
        item_list.append(item)

    # pylint: disable=star-args
    return SearchResult(item_list, **metadata)


def get_albums_for_artist(speaker, artist,
                          start=0, max_items=100, full_album_art_uri=False):
    """Search for an artist's albums.

    Parameters:
        artist: Artist name
        start (int): The starting index of the results
        max_items (int): The maximum number of items to return
        full_album_art_uri(bool): If the album art URI should include the
            IP address

    Returns:
        dict: A list of :py:class:`~.soco.data_structures.MLAlbum` object

    Raises:
        SoCoUPnPException: With ``error_code='701'`` if the item cannot be
            found
    """
    search = u'A:ALBUMARTIST/' + _escape_path(artist)

    response, _ = speaker._music_lib_search(search, start, max_items)

    # Parse the results
    dom = XML.fromstring(really_utf8(response['Result']))
    item_list = []
    for container in dom:
        item = get_didl_object(container)
        # this does not work: item is MLAlbum
        if item.item_class == 'object.container.album.musicAlbum':
            # Check if the album art URI should be fully qualified
            if full_album_art_uri:
                speaker._update_album_art_to_full_uri(item)
            item_list.append(item)

    # pylint: disable=star-args
    return item_list


def get_tracks_for_album(speaker, artist, album,
                          start=0, max_items=100, full_album_art_uri=False):
    """Search for an artist's albums.

    Parameters:
        artist: Artist name
        album: Album name
        start (int): The starting index of the results
        max_items (int): The maximum number of items to return
        full_album_art_uri(bool): If the album art URI should include the
            IP address

    Returns:
        dict: A list of :py:class:`~.soco.data_structures.MLTrack` object

    Raises:
        SoCoUPnPException: With ``error_code='701'`` if the item cannot be
            found
    """
    search = u'A:ALBUMARTIST/' + _escape_path(artist)
    search += u'/' + _escape_path(album)

    response, _ = speaker._music_lib_search(search, start, max_items)

    # Parse the results
    dom = XML.fromstring(really_utf8(response['Result']))
    item_list = []
    for container in dom:
        item = get_didl_object(container)
        # this does not work: item is MLTrack
        if item.item_class == 'object.item.audioItem.musicTrack':
            # Check if the album art URI should be fully qualified
            if full_album_art_uri:
                speaker._update_album_art_to_full_uri(item)
            item_list.append(item)

    # pylint: disable=star-args
    return item_list
