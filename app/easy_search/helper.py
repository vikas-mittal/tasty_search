import pandas as pd
import redis, json
from collections import Counter
import heapq

import constants as const

r = redis.Redis(host='localhost', port=6379, db=0)


def dump_to_json(object):
    """
    Dump string object to json
    :param object: json string
    :return: dumpped json object
    """
    return json.loads(json.dumps(object))
