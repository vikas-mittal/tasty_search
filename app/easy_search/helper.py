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
    insert_df_to_redis(df)
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


def convert_df_colm_to_list(df, col):
    """
    Convert given data frame column to list.
    :param df: data frame
    :param col: column of data frmae
    :return: list of column of data frame
    """
    return df[col].tolist()


def search_top_k_results(query_data_json):
    """
    It search the top k(20) results of reviews and summary together from the data stored in redis. For individual
    word in the query rank is calculated and top results are returned.
    :param query_data_json: Contains search query data in json format like {'data':'this is good product'}
    :return: top k(20) reviews that matches the search query in json format
    """
    query_data = dump_to_json(query_data_json)
    query_data_string = query_data["data"]
    each_word_json_review = get_json_formatted_data_from_redis("review_text_json")
    each_word_json_summary = get_json_formatted_data_from_redis("summary_text_json")
    rank_wise_reviews_review = get_search_string_rank_for_each_word(query_data_string, each_word_json_review)
    rank_wise_reviews_summary = get_search_string_rank_for_each_word(query_data_string, each_word_json_summary)
    merged_dict = merge_review_text_and_summary(rank_wise_reviews_review, rank_wise_reviews_summary)
    return top_k_matches(merged_dict)


def get_json_formatted_data_from_redis(obj_name):
    """
    Get data from redis based on object name
    :param obj_name: object nae which is stored in redis
    :return: data stored in redis with given obj name
    """
    return r.get(obj_name)


def insert_json_data_to_redis(json_data, obj_name):
    """
    Insert data into redis with given object name
    :param json_data: data to be inserted in redis
    :param obj_name: object name with which data need to be inserted
    """
    r.set(obj_name, json.dumps(json_data, encoding='latin1'))


def convert_data_in_df():
    """
    Convert data in the file into data frame.
    :return: data frame of the data in the file.
    """
    col_names = const.col_names
    df = pd.DataFrame(columns=col_names)
    list_of_lists = []
    with open(const.data_file_path) as f:
        for line in f:
            inner_list = [line.strip() for line in line.split(':')]
            if len(inner_list) > 1:
                list_of_lists.append(str(inner_list[1]))
            else:
                df = df.append(pd.DataFrame([list_of_lists], columns=col_names), ignore_index=True)
                list_of_lists = []
    return df


def get_json_of_each_word_occurrence_for_each_product(df, col):
    """
    For every word a json is created to find how many time that word is occurred in different products. A dictionary
    for the same is created.
    :param df: data frame
    :param col: column of which dictionary has to be made
    :return: dictionary each word occurrence in the different products.
    """
    text_list = df[col].tolist()
    each_word_occ_dict = {}
    for i in range(0, len(text_list)):
        list_on = text_list[i].split()
        for j in list_on:
            each_word_occ_dict.setdefault(j, []).append(i)
            each_word_occ_dict[j] = list(set(each_word_occ_dict[j]))

    return each_word_occ_dict


def get_search_string_rank_for_each_word(search_string, each_word_json):
    """
    For each word in the search string, it's occurrence in different products is calculated and accordingly product
    rank according to search string is stored.
    :param search_string: User Search string
    :param each_word_json: Dictionary of every word in which product it has occurred.
    :return: Dictionary which has every work rank of every product according to search string.
    """
    each_word_json = json.loads(each_word_json)
    document_rank_list = {}
    search_string_list = list(set(search_string.split()))
    for st in search_string_list:
        if st in each_word_json:
            for pro_id in each_word_json[st]:
                document_rank_list.setdefault(pro_id, 0)
                document_rank_list[pro_id] = document_rank_list[pro_id] + 1

    return document_rank_list


def merge_review_text_and_summary(review_text_json, summary_text_json):
    """
    Merged two dictionaries(review text dict and summary text dict) which contain rank of each product according to
    search query.
    :param review_text_json: Dictionary of review
    :param summary_text_json: Dictionary of summary
    :return: Merged dictionary of both
    """
    merged_dict = dict(Counter(review_text_json) + Counter(summary_text_json))
    return merged_dict


def top_k_matches(merged_dict):
    """
    Finding products which matches the best according to the search string by retrieving data frame from redis and
    sorting dictionary based on max rank of product review and summary.
    :param merged_dict: Dictionary containing review and summary rank of each product
    :return: Dictionary of top k(20) matches product according to the search query.
    """
    data_list = {}
    df = pd.read_msgpack(r.get("df"))
    largest_data = heapq.nlargest(20, merged_dict, key=merged_dict.get)
    for index, value in enumerate(largest_data):
        data_list[index] = (df.iloc[int(value)]).tolist()

    return data_list
