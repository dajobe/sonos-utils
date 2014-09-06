#!/usr/bin/python

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


logger = logging.getLogger('sonos-playlists')


def find_coordinator():
  """ Find coordinator speaker """
  for speaker in soco.discover():
    if speaker.is_coordinator:
      return speaker
  return None


def find_playlist(speaker, title):
  """ Find playlist by title """
  result = None
  for playlist in speaker.get_sonos_playlists():
    if playlist.title == title:
      result = playlist
      break

  return result


def inspect_playlist(speaker, playlist):
  print "Found sonos playlist %s - '%s' " % (playlist.item_id, playlist.title)

  batch_size=300
  start=0
  total=None

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
      print "  %4d %s - %s / %s seen first at %d" % (i, item.title, item.album, item.creator, first_i)


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
      level=logging.DEBUG
    else:
      level=logging.ERROR
    logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s', level=level)

    try:
      coord = find_coordinator()
      if coord is not None:
        for title in titles:
          playlist = find_playlist(coord, title)
          if playlist is None:
            logger.error("Could not find sonos playlist with title '%s'", title)
            sys.exit(1)
          else:
            inspect_playlist(coord, playlist)
    except requests.packages.urllib3.exceptions.ProtocolError, e:
      logger.error("Network error: %s",str(e))
      sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
