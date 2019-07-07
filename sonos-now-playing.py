#!/usr/bin/python
""" Get what is currenty playing """

# system
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# local
import json
import soco
import requests.packages.urllib3.exceptions

from common import find_all_coordinators


try:
  (speakers, coords) = find_all_coordinators()
  if speakers is None:
      raise Exception("Could not find any speakers")
  if len(coords) == 0:
      raise Exception("Could not find any coordinators in speakers")

  PLAY_STATE_LABELS = {
    'STOPPED' :         'Stopped',
    'PAUSED_PLAYBACK' : 'Paused',
    'PLAYING' :         'Playing'
  }


  for c in coords:
    group_label = c.group.short_label

    trans_info = c.get_current_transport_info()
    track_info = c.get_current_track_info()

    queue_size = c.queue_size

    play_state = trans_info['current_transport_state']
    play_state_label = PLAY_STATE_LABELS.get(play_state, play_state)

    if play_state != 'STOPPED' and track_info['title'] != '':
      track = track_info['title'] + ' - ' + track_info['album'] + ' / ' + track_info['artist']
      track += '   ' + track_info['position'] + ' / ' + track_info['duration']
      track_str = json.dumps(track_info)
    else:
      track = ''
      track_str = ''

    if c.is_playing_tv:
      line = u"{0:15s}: Playing TV".format(group_label)
    else:
      line = u"{0:15s}: {1:<7s} Track: {2} (Queue {3})".format(group_label,
                                                               play_state_label,
                                                               track,
                                                               queue_size)
    print line
    print '#JSON: ' + track_str.replace('\n', ' ')

except requests.packages.urllib3.exceptions.ProtocolError, e:
  print "Network error: " + str(e)
