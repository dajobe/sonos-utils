#!/usr/bin/python
"""
Inspect sonos playlists

USAGE: sonos-playlists.py [OPTIONS] TITLE...

OPTIONS:
  -h / --help  show help messsage
  -d / --debug enable debug messages 

If No TITLEs are given, all the known sonos playlist titles are shown.

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

from common import get_queue_size, is_playing_tv, find_all_coordinators, get_all_playlist_items

LOGGER = logging.getLogger('sonos-playlists')


class InspectSonosPlaylist(object):
  """ Inspect sonos playlists """

  def __init__(self):
    self.speakers = None
    self.coord = None
    self.playlists = None

  def find_coordinator(self):
    """ Find coordinator speaker """
    if self.coord is not None:
      return self.coord

    (self.speakers, coords) = find_all_coordinators()
    if len(coords) > 0:
      self.coord = coords[0]
    return self.coord


  def get_playlists(self, speaker):
    """ Find sonos playlists """
    if self.playlists is None:
      self.playlists = speaker.get_sonos_playlists()
    return self.playlists


  def find_playlist(self, speaker, title):
    """ Find sonos playlist by title """
    result = None
    for playlist in self.get_playlists(speaker):
      if playlist.title == title:
        result = playlist
        break

    return result


  def get_all_playlist_items(self, speaker, playlist):
    """ get a list of all items in the given playlist """
    playlist_items = get_all_playlist_items(speaker, playlist)
    print "Playlist '{0} has {0} items" .format(playlist.title, 
                                                len(playlist_items))
    return playlist_items


  def dedup_items(self, playlist_items):
    """ Dedup palylist items

    Returns tuple of (list of (index, item, original_index), unique items)
    """

    index = 1
    duplicates = []
    unique_items = []
    seen = dict()
    for item in playlist_items:
      if item.uri in seen:
        duplicates.append((index, item, seen[item.uri]))
      else:
        seen[item.uri] = index
        unique_items.append(item)
      index += 1

    return (duplicates, unique_items)

  def inspect_playlist(self, speaker, playlist):
    """ Inspect a sonos playlist """
    print "Found sonos playlist {0} - '{0}' ".format(playlist.item_id,
                                                     playlist.title)

    playlist_items = self.get_all_playlist_items(speaker, playlist)

    (duplicates, unique_items) = self.dedup_items(playlist_items)
    index = 1
    for item in unique_items:
      print "{0:4d} {1} - {2} / {3}".format(index, item.title, item.album,
                                             item.creator)
      index += 1

    if len(duplicates) > 0:
      print "\nPlaylist has {0} duplicates".format(len(duplicates))
      for (index, item, first_index) in duplicates:
        print "  {0:4d} {1} - {2} / {3} seen first at {4}".format(index,
                                                                  item.title,
                                                                  item.album,
                                                                  item.creator,
                                                                  first_index)

  def create_deduped_playlist(self, speaker, playlist, title):
    """ Create a new deduped sonos playlist

      :title Title of new playlist
    """
    playlist_items = self.get_all_playlist_items(speaker, playlist)

    (duplicates, unique_items) = self.dedup_items(playlist_items)

    def sort_item_key(item):
      "{1} / {2} / {3}".format(item.creator,
                               item.album if item.album else '',
                               item.title)

    sorted_playlist_items = sorted(unique_items, key=sort_item_key)

    print sorted_playlist_items[0]
    print sorted_playlist_items[0].item_id
    print sorted_playlist_items[0].didl_metadata
    return

    new_pl = speaker.create_sonos_playlist(title)
    for item in sorted_playlist_items:
      speaker.add_item_to_sonos_playlist(item, new_pl)

def main():
    """Main method"""

    parser = argparse.ArgumentParser(description='Inspect SONOS playlist')
    parser.add_argument('-d', '--debug',
                        action = 'store_true',
                        default = False,
                        help = 'debug messages (default: False)')

    parser.add_argument('titles', metavar='TITLE', nargs='*',
                        help='playlist title')
    args = parser.parse_args()

    debug = args.debug
    titles = args.titles
    ######################################################################

    if debug:
      level = logging.DEBUG
    else:
      level = logging.ERROR
    logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s', 
                        level = level)

    try:
      isp = InspectSonosPlaylist()
      coord = isp.find_coordinator()
      if coord is not None:
        print "Using coordinator speaker {0} - {1}".format(coord.player_name,
                                                           coord.ip_address)
        pl_titles = ["'" + pl.title + "'" for pl in isp.get_playlists(coord)]

        if len(titles) == 0:
          print "Known sonos playlists are: " + " ".join(pl_titles)
        else:
          for title in titles:
            playlist = isp.find_playlist(coord, title)
            if playlist is None:
              LOGGER.error("Could not find sonos playlist with title '{0}' - known ones are: {1}".format(title, " ".join(pl_titles)))
              sys.exit(1)
            else:
              isp.inspect_playlist(coord, playlist)
              # isp.create_deduped_playlist(coord, playlist, title + ' NEW')

      else:
        LOGGER.error("Could not find sonos coordinator speaker")

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
      LOGGER.error("Network error: " + str(exc))
      sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
