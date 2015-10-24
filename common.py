""" Common code not yet in SoCo """

# system
import re
import time
import urllib

import soco


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


def get_all_playlist_items(speaker, playlist):
    """ get a list of all items in the given playlist """
    batch_size = 400
    start = 0
    total = None

    playlist_items = []
    while True:
        out = speaker.music_library.browse(playlist, max_items=batch_size,
                                           start=start)
        if total is None:
            total = out.total_matches

        playlist_items += out[:]
        start += len(out)
        if start >= total:
            break

    return playlist_items
