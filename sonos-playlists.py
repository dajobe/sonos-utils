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


Logger = logging.getLogger('sonos-playlists')


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

    if self.speakers is None:
      self.speakers = soco.discover()

    for speaker in self.speakers:
      if speaker.is_coordinator:
        self.coord = speaker
        return self.coord
    return None


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


  def inspect_playlist(self, speaker, playlist):
    """ Inspect a sonos playlist """
    print "Found sonos playlist %s - '%s' " % (playlist.item_id, playlist.title)

    batch_size = 300
    start = 0
    total = None

    playlist_items = []
    while True:
      out = speaker.browse(playlist, max_items = batch_size, start=start)
      if total is None:
        total = out.total_matches
        print "Playlist %s has %d items" % (playlist.title, total)

      playlist_items += out[:]
      start += len(out)
      if start >= total:
        break

    i = 1
    duplicates = []
    seen = dict()
    for item in playlist_items:
      print "%4d %s - %s / %s" % (i, item.title, item.album, item.creator)
      if item.uri in seen:
        print "  DUPLICATE: seen first at %d" % (seen[item.uri], )
        duplicates.append((i, item, seen[item.uri]))
      else:
        seen[item.uri] = i
      i += 1

    if len(duplicates) > 0:
      print "\nPlaylist has %d duplicates" % (len(duplicates), )
      for (i, item, first_i) in duplicates:
        print "  %4d %s - %s / %s seen first at %d" % (i, item.title,
                                                       item.album,
                                                       item.creator, first_i)


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
        print "Using coordinator speaker %s - %s" % (coord.player_name,
                                                     coord.ip_address)
        pl_titles = ["'" + pl.title + "'" for pl in isp.get_playlists(coord)]

        if len(titles) == 0:
          print "Known sonos playlists are: " + " ".join(pl_titles)
        else:
          for title in titles:
            playlist = isp.find_playlist(coord, title)
            if playlist is None:
              Logger.error("Could not find sonos playlist with title '%s' - known ones are: %s", title, " ".join(pl_titles))
              sys.exit(1)
            else:
              isp.inspect_playlist(coord, playlist)
      else:
        Logger.error("Could not find sonos coordinator speaker")

    except requests.packages.urllib3.exceptions.ProtocolError, exc:
      Logger.error("Network error: %s", str(exc))
      sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
