import gzip
import json
import logging
import os
import tempfile
from typing import Dict

from model import Mask, Space


def jsonify(space: Space):
    return {k:{p.__hash__():l for p,l in v.items()} for k,v in space.items()}


def unjsonify(json_map: Dict):
    return {k:{Mask.numbered(p):l for p,l in v.items()} for k,v in json_map.items()}


def fetch_cache(game_id: str, gzipped=False):
    logging.debug("Loading cached decision tree for %s (faster than recalculating)..." % game_id)
    cachefile = get_cache_file(game_id, gzipped)
    if os.path.exists(cachefile):
        with do_open(cachefile, gzipped) as infile:
            return unjsonify(json.load(infile))
    return None


def get_cache_file(game_id: str, gzipped=False):
    logging.debug("Calculating hash for universe")
    hash_file_name = "slytherin-cache.%s.json%s" % (game_id, ".gz" if gzipped else "")
    cachefile = os.path.join(tempfile.gettempdir(), hash_file_name)
    logging.debug("Cache file is " + cachefile)
    return cachefile


def save_cache(game_id: str, data: Space, gzipped=False):
    logging.debug("Saving decision tree to cache... ")
    cachefile = get_cache_file(game_id, gzipped)
    with do_open(cachefile, gzipped, "w") as outfile:
        json.dump(jsonify(data), outfile)


def do_open(file: str, gzipped: bool, flag: str = "r"):
    if gzipped:
        return gzip.open(file, flag + "t")
    return open(file, flag)

