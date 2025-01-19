import csv
import json
import math
import os
from pathlib import Path

import chardet


class GoldenStandardLoader:
    """
    A class used to represent the golden standard (ground truth) of a dataset

    Attributes
    ----------
    expected_matches: set
        The expected matches in a set of frozensets
    size: int
        The size of the golden standard

    Methods
    -------
    load_golden_standard(path)
        Function that loads the golden standard from a JSON file

    is_in_golden_standard(): bool
        Function that checks if a mapping is in the golden standard
    """

    def __init__(self, path):
        """
        Parameters
        ----------
         path : str
            The path of the JSON file
        """
        self.expected_matches = set()
        self.size = 0
        self.load_golden_standard(path)

    def load_golden_standard(self, path: str):
        """
        Function that loads the golden standard from a JSON file

        Parameters
        ----------
        path : str
            The path of the JSON file
        """
        with open(path) as json_file:
            mappings: list = json.load(json_file)["matches"]
        for mapping in mappings:
            self.expected_matches.add(
                frozenset(
                    (
                        (mapping["source_table"], mapping["source_column"]),
                        (mapping["target_table"], mapping["target_column"]),
                    )
                )
            )
        self.size = len(self.expected_matches)

    def is_in_golden_standard(self, mapping: set):
        """
        Function that checks if a mapping is in the golden standard

        Parameters
        ----------
        mapping : set
            The mapping that we want to check

        Returns
        -------
        bool
            True if the mapping is in the golden standard false if not
        """
        return mapping in self.expected_matches


def is_sorted(dictionary: dict):
    """
    Function that checks if a dict is sorted (true if sorted false if not)

    Parameters
    ----------
    dictionary: dict
        The dict to check

    Returns
    -------
    bool
        If the dict is sorted or not
    """
    prev = None
    for value in dictionary.values():
        if prev is None:
            prev = value
        else:
            if prev > value:
                return False
    return True


def convert_data_type(value: str):
    """
    Takes a value as a string and return it with its proper datatype attached

    Parameters
    ----------
    value: str
        The value that we want to find its datatype as a string

    Returns
    -------
    The value with the proper datatype
    """
    try:
        f = float(value)
        if f.is_integer():
            return int(f)
        return f
    except ValueError:
        return value


def get_project_root():
    """Return the root of the project as a string"""
    return str(Path(__file__).parent.parent)


def get_relative_path(path: str):
    """Return the relative path of a file from the project root"""
    return os.path.relpath(path, get_project_root())


def create_folder(path: str):
    """Create a folder on the given path"""
    if not os.path.exists(path):
        os.makedirs(path)


# def one_to_one_matches(matches: dict):
#     """
#     A filter that takes a dict of column matches and returns a dict of 1 to 1 matches. The filter works in the following
#     way: At first it gets the median similarity of the set of the values and removes all matches
#     that have a similarity lower than that. Then from what remained it matches columns for me highest similarity
#     to the lowest till the columns have at most one match.

#     Parameters
#     ----------
#     matches : dict
#         The ranked list of matches

#     Returns
#     -------
#     dict
#         The ranked list of matches after the 1 to 1 filter
#     """
#     set_match_values = set(matches.values())

#     if len(set_match_values) < 2:
#         return matches

#     matched = dict()
#     for key in matches.keys():
#         matched[key[0]] = False
#         matched[key[1]] = False

#     median = list(set_match_values)[math.ceil(len(set_match_values)/2)]
#     print('median',median)
#     matches1to1 = dict()

#     for key in matches.keys():
#         if (not matched[key[0]]) and (not matched[key[1]]):
#             similarity = matches.get(key)
#             if similarity >= median:
#                 matches1to1[key] = similarity
#                 matched[key[0]] = True
#                 matched[key[1]] = True
#             else:
#                 break
#     return matches1to1


def one_to_one_matches(matches: dict):
    """
    A filter that takes a dict of column matches and returns a dict of 1 to 1 matches. The filter works in the following
    way: At first it gets the median similarity of the set of the values and removes all matches
    that have a similarity lower than that. Then from what remained it matches columns for me highest similarity
    to the lowest till the columns have at most one match.
    Parameters
    ----------
    matches : dict
        The ranked list of matches
    Returns
    -------
    dict
        The ranked list of matches after the 1 to 1 filter
    """
    set_match_values = set(matches.values())
    set_match_values = matches.values()

    if len(set_match_values) < 2:
        return matches

    matched = dict()

    for key in matches.keys():
        matched[key[0]] = False
        matched[key[1]] = False

    median = list(set_match_values)[math.ceil(len(set_match_values) / 2)]

    matches1to1 = dict()

    for key in matches.keys():
        if (not matched[key[0]]) and (not matched[key[1]]):
            similarity = matches.get(key)
            if similarity >= median:
                matches1to1[key] = similarity
                matched[key[0]] = True
                matched[key[1]] = True
            else:
                break
    return matches1to1


def get_table_from_dataset_path(ds_path: str):
    """Returns the table name from the dataset path"""
    return ds_path.split(".")[0].split("/")[-1]


def get_encoding(ds_path: str) -> str:
    """Returns the encoding of the file"""
    with open(ds_path, "rb") as f:
        return chardet.detect(f.read())["encoding"]


def get_delimiter(ds_path: str) -> str:
    """Returns the encoding of the csv file"""
    with open(ds_path) as f:
        first_line = f.readline()
        s = csv.Sniffer()
        return s.sniff(first_line).delimiter


def get_tp_fn(matches: dict, golden_standard: GoldenStandardLoader, n: int = None):
    """
    Calculate the true positive  and false negative numbers of the given matches

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    n : int, optional
        The percentage number that we want to consider from the ranked list (matches)
        e.g. (90) for 90% of the matches

    Returns
    -------
    (int, int)
        True positive and false negative counts
    """
    tp = 0
    fn = 0
    all_matches = list(map(lambda m: frozenset(m), list(matches.keys())))
    if n is not None:
        n = int(n)
        all_matches = all_matches[:n]
    for expected_match in golden_standard.expected_matches:
        if expected_match in all_matches:
            tp = tp + 1
        else:
            fn = fn + 1
    return tp, fn


def get_fp(matches: dict, golden_standard: GoldenStandardLoader, n: int = None):
    """
    Calculate the false positive number of the given matches

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    n : int, optional
        The percentage number that we want to consider from the ranked list (matches)
        e.g. (90) for 90% of the matches

    Returns
    -------
    int
        False positive
    """
    fp = 0

    all_matches = list(map(lambda m: frozenset(m), list(matches.keys())))

    if n is not None:
        all_matches = all_matches[:n]

    for possible_match in all_matches:
        if possible_match not in golden_standard.expected_matches:
            fp = fp + 1
    return fp


def recall(matches: dict, golden_standard: GoldenStandardLoader, one_to_one=False):
    """
    Function that calculates the recall of the matches against the golden standard. If one_to_one is set to true, it
    also performs an 1-1 match filer. Meaning that each column will match only with another one.

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    one_to_one : bool, optional
        If to perform the 1-1 match filter

    Returns
    -------
    float
        The recall
    """
    if one_to_one:
        matches = one_to_one_matches(matches)
    tp, fn = get_tp_fn(matches, golden_standard)
    if tp + fn == 0:
        return 0
    return tp / (tp + fn)


def precision(matches: dict, golden_standard: GoldenStandardLoader, one_to_one=False):
    """
    Function that calculates the precision of the matches against the golden standard. If one_to_one is set to true, it
    also performs an 1-1 match filer. Meaning that each column will match only with another one.

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    one_to_one : bool, optional
        If to perform the 1-1 match filter

    Returns
    -------
    float
        The precision
    """
    if one_to_one:
        matches = one_to_one_matches(matches)
    tp, fn = get_tp_fn(matches, golden_standard)
    fp = get_fp(matches, golden_standard)
    if tp + fp == 0:
        return 0
    return tp / (tp + fp)


def f1_score(matches: dict, golden_standard: GoldenStandardLoader, one_to_one=False):
    """
    Function that calculates the F1 score of the matches against the golden standard. If one_to_one is set to true, it
    also performs an 1-1 match filer. Meaning that each column will match only with another one.

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    one_to_one : bool, optional
        If to perform the 1-1 match filter

    Returns
    -------
    float
        The f1_score
    """
    pr = precision(matches, golden_standard, one_to_one)
    re = recall(matches, golden_standard, one_to_one)
    if pr + re == 0:
        return 0
    return 2 * ((pr * re) / (pr + re))


def precision_at_n_percent(
    matches: dict, golden_standard: GoldenStandardLoader, n: int
):
    """
    Function that calculates the precision at n %
    e.g. if n is 10 then only the first 10% of the matches will be considered for the precision calculation

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard
    n : int
        The integer percentage number

    Returns
    -------
    float
        The precision at n %
    """
    # number_to_keep = int(math.ceil((n / 100) * len(matches.keys())))
    number_to_keep = n
    tp, fn = get_tp_fn(matches, golden_standard, number_to_keep)
    fp = get_fp(matches, golden_standard, number_to_keep)
    if tp + fp == 0:
        return 0
    return tp / (tp + fp)


def recall_at_sizeof_ground_truth(matches: dict, golden_standard: GoldenStandardLoader):
    """
    Function that calculates the recall at the size of the ground truth.
    e.g. if the size of ground truth size is 10 then only the first 10 matches will be considered for
    the recall calculation

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard

    Returns
    -------
    float
        The recall at the size of ground truth
    """
    tp, fn = get_tp_fn(matches, golden_standard, golden_standard.size)
    if tp + fn == 0:
        return 0
    return tp / (tp + fn)


def compute_accuracy(matches: dict, golden_standard: GoldenStandardLoader):
    """
    Function that calculates the accuracy for schema matching based on predicted matches
    and the golden standard using existing functions for TP, FP, and FN.

    Parameters
    ----------
    matches : dict
        Dictionary of predicted matches where keys are tuples of (source_column, target_column), and values are similarity scores.
    golden_standard : GoldenStandardLoader
        Object that contains the golden standard (ground truth) matches.

    Returns
    -------
    float
        The accuracy of the predicted matches.
    """
    # Use the existing get_tp_fn() function to get TP (True Positives) and FN (False Negatives)
    tp, fn = get_tp_fn(matches, golden_standard)

    # Use the existing get_fp() function to get FP (False Positives)
    fp = get_fp(matches, golden_standard)

    # Accuracy = TP / (TP + FP + FN)
    total_predictions = tp + fp + fn

    if total_predictions == 0:
        return 0.0  # To avoid division by zero

    accuracy = tp / total_predictions
    return accuracy


def dcg_at_n(matches: dict, golden_standard: GoldenStandardLoader, n: int = None):
    """
    Compute the Discounted Cumulative Gain (DCG) at n.

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower.
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard.
    n : int, optional
        The number of top-ranked items to consider for DCG (default is None, which considers all matches).

    Returns
    -------
    float
        The DCG score.
    """
    dcg = 0.0
    all_matches = list(matches.keys())

    if n is not None:
        all_matches = all_matches[:n]

    for i, match in enumerate(all_matches):
        if frozenset(match) in golden_standard.expected_matches:
            dcg += 1 / math.log2(i + 2)  # Log base 2, starting at index 2 for ranking

    return dcg


def idcg_at_n(golden_standard: GoldenStandardLoader, n: int):
    """
    Compute the Ideal Discounted Cumulative Gain (IDCG) at n.

    Parameters
    ----------
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard.
    n : int
        The number of top-ranked items to consider for IDCG.

    Returns
    -------
    float
        The IDCG score.
    """
    idcg = 0.0
    for i in range(min(n, golden_standard.size)):
        idcg += 1 / math.log2(i + 2)  # Log base 2, starting at index 2 for ranking

    return idcg


def NDCG_at_n(
    matches: dict,
    golden_standard: GoldenStandardLoader,
    n: int = None,
    one_to_one=False,
):
    """
    Compute the Normalized Gain Cumulated Discount (NDCG) at n with an optional one-to-one match condition.

    Parameters
    ----------
    matches : dict
        Ranked list of matches from the match with higher similarity to lower.
    golden_standard : GoldenStandardLoader
        An object that contains all the information about the golden standard.
    n : int, optional
        The number of top-ranked items to consider for NDCG (default is None, which considers all matches).
    one_to_one : bool, optional
        If True, apply one-to-one matching with the median similarity threshold and set n to None.

    Returns
    -------
    float
        The NDCG score.
    """
    m = len(matches)
    if one_to_one:
        # Apply one-to-one filtering and set n to None
        matches = one_to_one_matches(matches)

    dcg = dcg_at_n(matches, golden_standard, n)
    idcg = idcg_at_n(golden_standard, m)

    if idcg == 0:
        return 0.0

    return dcg / idcg
