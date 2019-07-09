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


def restructure_data_and_insert_in_redis():
    """
    It convert the data stored in file into data frame. Also create a dictionary for each word occurrence in the
    data frame in review text and summary text. At the end insert those into redis for future use.
    """
    df = convert_data_in_df()
    review_each_word_occ_dict = get_json_of_each_word_occurrence_for_each_product(df, const.review_text_col_name)
    summary_each_word_occ_dict = get_json_of_each_word_occurrence_for_each_product(df, const.summary_text_col_name)
    insert_json_data_to_redis(review_each_word_occ_dict, "review_text_json")
    insert_json_data_to_redis(summary_each_word_occ_dict, "summary_text_json")


def insert_df_to_redis(df):
    """
    Insert Data frame in redis with object name 'df' for future use of data frame.
    :param df: data frame
    :return:
    """
    r.set("df", df.to_msgpack(compress='zlib'))
