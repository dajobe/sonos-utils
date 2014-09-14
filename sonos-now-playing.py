#!/usr/bin/python
""" Get what is currenty playing """

# system
import sys
import time
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# local
import soco
import requests.packages.urllib3.exceptions

from common import get_queue_size, is_playing_tv


try:
  for count in range(0, 5):
    speakers = soco.discover()
    if speakers is not None:
      break
    time.sleep(1)
  if speakers is None:
    raise "Could not find any speakers"

  coords = [s for s in speakers if s.is_coordinator]

  if len(coords) == 0:
    raise "Could not find any coordinators in speakers"

  PLAY_STATE_LABELS = {
    'STOPPED' :         'stopped',
    'PAUSED_PLAYBACK' : 'paused',
    'PLAYING' :         'playing'
  }


  for c in coords:

    # Make a "Sonos" like group label
    group_names = sorted([m.player_name for m in c.group.members])
    group_label = group_names[0]
    if len(group_names) > 1:
      group_label += " + %d" % (len(group_names)-1, )

    trans_info = c.get_current_transport_info()
    track_info = c.get_current_track_info()

    queue_size = get_queue_size(c)

    play_state = trans_info['current_transport_state']
    play_state_label = PLAY_STATE_LABELS.get(play_state, play_state)

    if play_state != 'STOPPED' and track_info['title'] != '':
      track = track_info['title'] + ' - ' + track_info['album'] + ' / ' + track_info['artist']
      track += '   ' + track_info['position'] + ' / ' + track_info['duration']
    else:
      track = ''

    if is_playing_tv(c):
      line = "%15s  Playing TV" % (group_label, )
    else:
      line = "%15s  %7s  %s (Queue %d)" % (group_label, play_state_label, track, queue_size)
    print line

except requests.packages.urllib3.exceptions.ProtocolError, e:
  print "Network error: %s" % (str(e), )
