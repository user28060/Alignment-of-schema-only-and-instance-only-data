import os

import pandas as pd
from tqdm import tqdm

from schema_instance.schema_instance_gpt.matchers import (
    instance_instance_matcher,
    schema_inst_schema_ins_matcher,
    schema_schema_matcher,
    type_matcher,
    validate_rule_bool,
)
from schema_instance.schema_instance_gpt.utils import (
    compute_metrics,
    open_or_generate_matcher_with_best_option,
    save_embeddings,
    save_matchers,
    update_matchers,
)


def process_matcher(matcher_name, matcher_func, matcher_args, path, model_name, name):
    """
    Traite l'ouverture ou la génération d'un matcher donné. Si les fichiers "best" ou "fallback"
    ne sont pas trouvés, génère les données via `matcher_func` et remplace `fallback_variable` par le résultat.
    """
    matcher_path = os.path.join(path, model_name, matcher_name, f"{name}.json")
    best_matcher_path = os.path.join(
        path, model_name, "best", matcher_name, f"{name}.json"
    )
    # Ouvrir ou générer les données
    matcher_result, return_flag = open_or_generate_matcher_with_best_option(
        best_matcher_path, matcher_path, matcher_func, *matcher_args
    )

    # Si le fichier n'a pas été trouvé, remplacer la variable de fallback par les résultats générés

    if return_flag:
        matcher_result = {
            tuple(item["Key"]): item["Value"]
            for item in matcher_result
            if isinstance(item["Key"], list)
        }

    return matcher_result, return_flag


def match_sources(
    attributes_s1,
    extended_sc1,
    generated_instances_s1,
    instances_s2,
    generated_attributes_s2,
    fake_attributes_s2,
    types1,
    types2,
    name_s1,
    name_s2,
    categorie_dataset_name,
    model_name,
    mapping_path,
    key_api_gpt,
    path="./tests/outputs/",
):
    """
    Matches attributes between SC1 and SC2 based on type and similarity.

    Args:
    attributes_s1 (list): A list of attribute names from SC1.
    generated_attributes_s2 (list): A list of generated attributes from SC2.
    fake_attributes_s2 (list): Fake attributes corresponding to SC2.
    types1 (list): Data types of SC1 attributes.
    types2 (list): Data types of SC2 attributes.
    model_name (str): The name of the model for similarity matching.

    Returns:
    dict: A dictionary of matched attributes between SC1 and SC2.
    """
    matches = {}
    matcher1 = {}
    matcher2 = {}
    matcher3 = {}
    matcher4 = {}
    matcher5 = {}

    df_DS1 = pd.DataFrame()
    df_DS2 = pd.DataFrame()

    for idx, (attr_s1, attr_s1_ext, gen_instances_i_s1) in tqdm(
        enumerate(
            zip(attributes_s1, extended_sc1.values(), generated_instances_s1.values())
        ),
        total=len(attributes_s1),
    ):

        for i, (instances_i_s2, gen_attrs_s2) in enumerate(
            zip(instances_s2, generated_attributes_s2.values())
        ):
            if type_matcher(types1[idx], types2[i]):  # first matcher constrainst

                validate_rule = validate_rule_bool(
                    attr_s1,
                    name_s1,
                    categorie_dataset_name,
                    types1,
                    idx,
                    instances_i_s2,
                )
                try:
                    similarity_sch_sch = schema_schema_matcher(
                        gen_attrs_s2, [attr_s1] + [attr_s1_ext], model_name
                    )  # third matcher domain knowledge
                except Exception:
                    similarity_sch_sch = 0
                try:
                    similarity_ins_ins = instance_instance_matcher(
                        gen_instances_i_s1, instances_i_s2, model_name
                    )  # fourth matcher domain knowledge
                except Exception:
                    similarity_ins_ins = 0

                similarity_sc_ins_sc_ins, df_DS1, df_DS2 = (
                    schema_inst_schema_ins_matcher(
                        attr_s1,
                        attr_s1_ext,
                        gen_instances_i_s1,
                        gen_attrs_s2,
                        instances_i_s2,
                        model_name,
                        df_DS1,
                        df_DS2,
                        fake_attributes_s2[i],
                    )
                )  # fifth matcher domain knowledge

                (
                    matches,
                    matcher1,
                    matcher2,
                    matcher3,
                    matcher4,
                    matcher5,
                ) = update_matchers(
                    attr_s1,
                    fake_attributes_s2[i],
                    matches,
                    matcher1,
                    matcher2,
                    matcher3,
                    matcher4,
                    matcher5,
                    1,
                    validate_rule,
                    similarity_sch_sch,
                    similarity_ins_ins,
                    similarity_sc_ins_sc_ins,
                )

            else:
                (
                    matches,
                    matcher1,
                    matcher2,
                    matcher3,
                    matcher4,
                    matcher5,
                ) = update_matchers(
                    attr_s1,
                    fake_attributes_s2[i],
                    matches,
                    matcher1,
                    matcher2,
                    matcher3,
                    matcher4,
                    matcher5,
                    0,
                    0,
                    0,
                    0,
                    0,
                )
                matches[(attr_s1, fake_attributes_s2[i])] = 0
    save_matchers(
        model_name,
        matcher1,
        matcher2,
        matcher3,
        matcher4,
        matcher5,
        name_s1,
    )
    save_embeddings(
        df_DS1,
        df_DS2,
        model_name,
        name_s1,
    )
    print("heeeey")
    return compute_metrics(name_s1, name_s2, mapping_path, matches, model_name)
