""" Common code not yet in SoCo """

from soco.utils import really_utf8
from soco.xml import XML

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

def get_all_queue_items(speaker, playlist):
    """ get a list of all items in the queue """
    batch_size = 400
    start = 0
    total = None

    playlist_items = []
    while True:
        out = speaker.get_queue(max_items=batch_size, start=start)
        if total is None:
            total = out.total_matches
            print "Playlist %s has %d items" % (playlist.title, total)

        playlist_items += out[:]
        start += len(out)
        if start >= total:
            break

    return playlist_items

