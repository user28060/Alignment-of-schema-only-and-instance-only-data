import ast
import json
import os
import re

import numpy as np
import pandas as pd

from schema_instance.schema_instance_llama.metrics_val import (
    GoldenStandardLoader,
    f1_score,
    precision,
    recall,
)


def extract_dictionary_from_response(response_text):
    """
    This function cleans and extracts the dictionary part from the GPT response.
    """
    print("response_text", response_text)
    dict_match = re.search(r"({.*})", response_text, re.DOTALL)

    if dict_match:
        dictionary_string = dict_match.group(1)
        try:
            schema_match = ast.literal_eval(dictionary_string)
            return schema_match
        except (SyntaxError, ValueError) as e:
            print(f"Error evaluating dictionary: {e}")
            return {}
    else:
        print("No dictionary found in the response.")
        return {}


def get_matches(list_matchs, name_s1, name_s2):
    source_table = name_s1 + "_source"
    target_table = name_s2 + "_target"
    output_matches = {}

    # Use numpy arrays for vectorized processing of matches
    source_columns = np.array(list(list_matchs.keys()))[:, 0]
    target_columns = np.array(list(list_matchs.keys()))[:, 1]
    scores = np.array(list(list_matchs.values()))

    for source_column, target_column, score in zip(
        source_columns, target_columns, scores
    ):
        output_matches[
            ((source_table, source_column), (target_table, target_column))
        ] = score

    return output_matches


def compute_metrics(name_s1, name_s2, mapping_path, list_matchs, model_name):
    path= os.getcwd().split('/')
    i=path.index('Alignment-of-schema-only-and-instance-only-data')
    folder_path= "/".join(path[:i+1])
    
    list_matchs = dict(
        sorted(list_matchs.items(), key=lambda item: item[1], reverse=True)
    )
    matches = get_matches(list_matchs, name_s1, name_s2)
    gold = GoldenStandardLoader(mapping_path)
    results = (
        precision(matches, gold, one_to_one=True),
        recall(matches, gold, one_to_one=True),
        f1_score(matches, gold, one_to_one=True),
    )
    mapping_path = os.path.join(
        folder_path + "/tests/outputs",
        model_name + "/matches",
        f"{name_s1}.json",
    )

    # Normaliser et sauvegarder le mapping
    mapping_normalized = pd.json_normalize(matches)
    mapping_normalized_json = mapping_normalized.to_json(orient="records", indent=4)

    with open(mapping_path, "w") as f:
        f.write(mapping_normalized_json)

    return results


def make_valid_identifier(name):
    """
    Convertit une chaîne en un identifiant valide pour Python.
    """
    return re.sub(r"\W|^(?=\d)", "_", name)


def is_safe_code(code):
    """
    Vérifie si le code ne contient pas de structures dangereuses.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["open", "os", "subprocess", "system", "eval"]:
                    return False
        return True
    except Exception as e:
        print(f"Erreur lors de l'analyse syntaxique: {e}")
        return False


def generate_and_store_function(function_code, function_name):
    rules_path = "rules.py"

    with open(rules_path, "a") as file:
        file.write("\n\n\n")
        file.write(function_code)

    with open(rules_path, "r") as file:
        content = file.read()

    if function_name in content:
        print(f"Validation function '{function_name}' successfully added to rules.py")
    else:
        print(f"Failed to add the function '{function_name}' to rules.py")


def update_matchers(
    a_s1,
    a_s2,
    matches,
    matcher1,
    matcher2,
    matcher3,
    matcher4,
    matcher5,
    m1,
    m2,
    m3,
    m4,
    m5,
):
    """
    Use numpy arrays for efficient storage and updates for matchers.
    """
    # Vectorizing matcher updates with numpy arrays
    # match_values = np.array([m1, m2, m3, m4, m5, m6, m7, m8])
    match_values = np.array([m1, m2, m3, m4, m5])
    avg_match_value = np.mean(match_values)

    matches[(a_s1, a_s2)] = avg_match_value
    matcher1[(a_s1, a_s2)] = m1
    matcher2[(a_s1, a_s2)] = m2
    matcher3[(a_s1, a_s2)] = m3
    matcher4[(a_s1, a_s2)] = m4
    matcher5[(a_s1, a_s2)] = m5

    return (
        matches,
        matcher1,
        matcher2,
        matcher3,
        matcher4,
        matcher5,
    )


def save_matchers(
    model_name,
    matcher1,
    matcher2,
    matcher3,
    matcher4,
    matcher5,
    name_s1,
    path="/tests/outputs/",
):
    path_= os.getcwd().split('/')
    i=path_.index('Alignment-of-schema-only-and-instance-only-data')
    folder_path= "/".join(path[:i+1]) + path
    """
    Optimized save function for matchers using numpy arrays.
    """
    # Convert matchers to DataFrames
    matcher_list = [
        matcher1,
        matcher2,
        matcher3,
        matcher4,
        matcher5,
    ]
    matcher_names = [
        "matcher1_type",
        "matcher2_rule",
        "matcher3_sch_sch",
        "matcher4_ins_ins",
        "matcher5_sch_ins_sch_ins",
    ]
    for i, matcher in enumerate(matcher_list):
        matcher_df = pd.DataFrame(list(matcher.items()), columns=["Key", "Value"])
        matcher_path = os.path.join(
            path, model_name + f"/{matcher_names[i]}", f"{name_s1}.json"
        )

        os.makedirs(os.path.dirname(matcher_path), exist_ok=True)
        matcher_df.to_json(matcher_path, orient="records", indent=4)

    print(f"Success: Matchers saved for {name_s1}")


def save_embeddings(
    df_DS1,
    df_DS2,
    model_name,
    name_s1,
    path="/tests/outputs/",
):
    """
    Optimized save function for matchers using numpy arrays.

    Parameters:
        df_DS1 (pd.DataFrame): DataFrame for dataset 1.
        df_DS2 (pd.DataFrame): DataFrame for dataset 2.
        model_name (str): Name of the model used to generate embeddings.
        name_s1 (str): Identifier for the saved file.
        path (str): Base path where files will be saved.
    """
    path_= os.getcwd().split('/')
    i=path_.index('Alignment-of-schema-only-and-instance-only-data')
    folder_path= "/".join(path[:i+1]) + path
    embeddings_list = [df_DS1, df_DS2]
    embeddings_names = ["Embedd_DS1", "Embedd_DS2"]

    for i, embed_df in enumerate(embeddings_list):
        embedding_dir = os.path.join(folder_path, model_name, embeddings_names[i])
        embedding_path = os.path.join(embedding_dir, f"{name_s1}.csv")
        os.makedirs(embedding_dir, exist_ok=True)

        # Save the DataFrame
        embed_df.to_csv(embedding_path, index=True)

    print(f"Success: Embeddings saved for {name_s1} in {path}")


def save_auxiliary_informations(
    extended_sc1,
    generated_attributes_s2,
    generated_instances_s1,
    name_s1,
    path="/tests/outputs/",
):
    """
    Save auxiliary information in JSON format.
    """
    path_= os.getcwd().split('/')
    i=path_.index('Alignment-of-schema-only-and-instance-only-data')
    folder_path= "/".join(path[:i+1]) + path
    
    extended_sc1_path = os.path.join(
        folder_path, "extanded_attributes", f"{name_s1}_extended_sc1.json"
    )
    generated_attributes_s2_path = os.path.join(
        folder_path, "generated_attributes", f"{name_s1}_generated_attributes_s2.json"
    )
    generated_instances_s1_path = os.path.join(
        folder_path, "generated_instances", f"{name_s1}_generated_instances_s1.json"
    )

    with open(extended_sc1_path, "w") as f:
        json.dump(extended_sc1, f, indent=4)

    with open(generated_attributes_s2_path, "w") as f:
        json.dump(generated_attributes_s2, f, indent=4)

    with open(generated_instances_s1_path, "w") as f:
        json.dump(generated_instances_s1, f, indent=4)


def process_match(match_dict, name_s1, name_s2):
    source_table = name_s1 + "_source"
    target_table = name_s2 + "_target"
    output_matches = {}

    sorted_matches = dict(
        sorted(match_dict.items(), key=lambda item: item[1], reverse=True)
    )
    for (source_column, target_column), score in sorted_matches.items():
        output_matches[
            ((source_table, source_column), (target_table, target_column))
        ] = score
    return output_matches


def open_or_generate_with_best_option(
    best_path, fallback_path, generate_func, *generate_args
):
    """
    Ouvre le fichier best_path s'il existe. Sinon, ouvre le fallback_path.
    Si aucun n'existe, génère les données et les sauvegarde dans fallback_path.
    """
    if os.path.exists(best_path):
        with open(best_path, "r") as f:
            return json.load(f), True
    elif os.path.exists(fallback_path):
        with open(fallback_path, "r") as f:
            return json.load(f), True
    else:
        data = generate_func(*generate_args)
        if data is not None:
            with open(fallback_path, "w") as f:
                json.dump(data, f)
            return data, False


def open_or_generate_matcher_with_best_option(
    best_path, fallback_path, generate_func, *generate_args
):
    """
    Ouvre le fichier best_path s'il existe. Sinon, ouvre le fallback_path.
    Si aucun n'existe, génère les données et les sauvegarde dans fallback_path.
    """
    if os.path.exists(best_path):
        with open(best_path, "r") as f:
            return json.load(f), True
    elif os.path.exists(fallback_path):
        with open(fallback_path, "r") as f:
            return json.load(f), True
    else:
        data = generate_func(*generate_args)
        return data, False
