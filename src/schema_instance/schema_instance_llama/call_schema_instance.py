import os
import time

import pandas as pd

from schema_instance.schema_instance_llama.data_preparation import prepare_data
from schema_instance.schema_instance_llama.generator import get_auxiliary_informations
from schema_instance.schema_instance_llama.similarity_calculations import match_sources


def schema_matching(
    input_file_s1, input_file_s2, model_name, categorie_dataset_name="Magellan"
):
    start_time = time.time()

    (
        name_s1,
        name_s2,
        input_file_s1,
        input_file_s2,
        mapping_path,
        attributes_s1,
        instances_s2,
        fake_attributes_s2,
        types1,
        types2,
    ) = prepare_data(input_file_s1, input_file_s2)
    extended_sc1, generated_attributes_s2, generated_instances_s1 = (
        get_auxiliary_informations(
            types1,
            name_s1,
            attributes_s1,
            fake_attributes_s2,
            instances_s2,
            types2,
            name_s2,
            categorie_dataset_name,
            "./tests/outputs",
        )
    )
    matches = match_sources(
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
    )

    end_time = time.time()
    print(
        f"Schema matching took {end_time - start_time:.2f} seconds"
    )  # Afficher la durée

    return matches


def process_file_llama(input_file_s1, input_file_s2, model_name, df):
    dataset_name = os.path.basename(input_file_s1).split(".")[0]

    # Vérification si l'entrée existe déjà
    exists = df.loc[
        (df["Dataset"] == dataset_name)
        & (df["generative_model"] == "GPT")
        & (df["embedding_model"] == model_name)
    ]

    if exists.empty:
        # Début de la mesure de temps pour schema_matching
        start_time = time.time()
        prec, rec, f1 = schema_matching(input_file_s1, input_file_s2, model_name)
        end_time = time.time()  # Fin de la mesure de temps
        execution_time = end_time - start_time
        new_row = pd.DataFrame(
            {
                "Dataset": [dataset_name],
                "generative_model": "Llama-3.2",
                "embedding_model": [model_name],
                "F1_Score": [f1],
                "Precision": [prec],
                "Recall": [rec],
                "Execution_Time": [execution_time],
            }
        )

        # Ajouter la nouvelle ligne au DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
        print(
            f"Model: {model_name} | Precision: {prec}, Recall: {rec}, F1: {f1} | Time: {execution_time:.2f} seconds"
        )
    return df
