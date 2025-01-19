import importlib

import numpy as np
import tiktoken
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer

from schema_instance.schema_instance_llama.cross_domain_embeddings import (
    get_embedding_hf,
    get_embedding_openai,
)
from schema_instance.schema_instance_llama.generator import (
    generate_validation_function,
    possibility_gen_rules_function,
)
from schema_instance.schema_instance_llama.utils import (
    generate_and_store_function,
    make_valid_identifier,
)


def count_tokens(text, model="gpt-3.5-turbo"):
    """
    Compte le nombre de tokens dans une chaîne de texte.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def truncate_text_to_limit(text, model="gpt-3.5-turbo", max_tokens=8000):
    """
    Tronque le texte pour qu'il respecte la limite de tokens.
    """
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)


models_transformers = [
    "bert-base-uncased",
    "roberta-base",
    "distilbert-base-uncased",
    "sentence-transformers/all-MiniLM-L6-v2",
    "albert-base-v2",
    "facebook/bart-base",
]


def type_matcher(source_type, target_type):
    """
    Checks if the type of the source and target attributes are compatible.

    Args:
    source_type (str): The type of the source attribute.
    target_type (str): The type of the target attribute.

    Returns:
    bool: True if types are compatible, False otherwise.
    """
    return source_type == target_type


def validate_rule(
    attribute_name, dataset_name, categorie_dataset_name, data_type, values
):
    if categorie_dataset_name == "Magellan":
        categorie_dataset_name = dataset_name

    valid_function_name = f"validate_{make_valid_identifier(attribute_name)}_{make_valid_identifier(categorie_dataset_name)}"
    with open(
        "./src/schema_instance/schema_instance_llama/rules.py",
        "r",
    ) as file:
        content = file.read()
    if valid_function_name not in content:
        result = possibility_gen_rules_function(
            attribute_name, categorie_dataset_name, data_type
        )
        if bool(result):
            # Générer le code de la fonction de validation
            validation_function_code = generate_validation_function(
                attribute_name, categorie_dataset_name, data_type
            )
            generate_and_store_function(validation_function_code, valid_function_name)
            # Importer dynamiquement le module rules après avoir ajouté la fonction
        else:
            print(
                f"La fonction '{valid_function_name}' n'a pas pu etre generée dans rules.py."
            )
            return None
    importlib.invalidate_caches()  # Assurez-vous que le cache de l'importation est mis à jour
    rules = importlib.import_module("src.schema_instance.schema_instance_llama.rules")
    importlib.reload(rules)  # Recharger le module `rules`
    validate_function = getattr(rules, valid_function_name, None)
    valid = None
    if validate_function:
        valid = validate_function(values)
    else:
        print(f"La fonction '{valid_function_name}' n'a pas été trouvée dans rules.py.")

    return valid


def validate_rule_bool(
    attr_s1, name_s1, categorie_dataset_name, types1, idx, instances_i_s2
):
    return_valid_rule = validate_rule(
        attr_s1, name_s1, categorie_dataset_name, types1[idx], instances_i_s2
    )
    validate = int(return_valid_rule is None or return_valid_rule)
    return validate


def schema_schema_matcher(generated_attrs_s2, attr_s1, model_name):
    """
    Computes the similarity between the generated attributes and SC1 attributes.

    Args:
    generated_attributes (list): A list of generated attribute names from SC2.
    attr_s1 (list): A list of attribute names from SC1.
    model_name (str): The name of the model to use for generating embeddings (e.g., "bert-base-uncased").

    Returns:
    float: The similarity score between the generated attributes and SC1 attributes.
    """
    attr_s1 = " ".join(attr_s1).replace("nan", "")
    generated_attrs_s2_combined = " ".join(generated_attrs_s2).replace("nan", "")

    # Use a model to calculate embeddings and similarity
    if model_name in models_transformers:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        embedding1 = get_embedding_hf(attr_s1, tokenizer, model)
        embedding2 = get_embedding_hf(generated_attrs_s2_combined, tokenizer, model)
        similarity = cosine_similarity(
            embedding1.reshape(1, -1), embedding2.reshape(1, -1)
        )[0][0]
        return similarity

    elif model_name == "gpt":
        max_tokens = 2000
        if count_tokens(attr_s1) > max_tokens:
            print(f"attr_s1 dépasse {max_tokens} tokens. Tronquage en cours...")
            attr_s1 = truncate_text_to_limit(attr_s1, max_tokens=max_tokens)
        if count_tokens(generated_attrs_s2_combined) > max_tokens:
            print(
                f"generated_attrs_s2_combined dépasse {max_tokens} tokens. Tronquage en cours..."
            )
            generated_attrs_s2_combined = truncate_text_to_limit(
                generated_attrs_s2_combined, max_tokens=max_tokens
            )

        embedding1 = get_embedding_openai(attr_s1)
        embedding2 = get_embedding_openai(generated_attrs_s2_combined)
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        similarity_score_openai = cosine_similarity(embedding1, embedding2)[0][0]
        return similarity_score_openai

    return 0


def instance_instance_matcher(generated_instances_s1, instances_s2, model_name):
    """
    Computes the similarity between the generated attributes and SC1 attributes.

    Args:
    generated_attributes (list): A list of generated attribute names from SC2.
    attr_s1 (list): A list of attribute names from SC1.
    model_name (str): The name of the model to use for generating embeddings (e.g., "bert-base-uncased").

    Returns:
    float: The similarity score between the generated attributes and SC1 attributes.
    """
    generated_instances_s1 = " ".join(map(str, generated_instances_s1)).replace(
        "nan", ""
    )
    instances_s2 = " ".join(map(str, instances_s2)).replace("nan", "")

    # Use a model to calculate embeddings and similarity
    if model_name in models_transformers:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        embedding1 = get_embedding_hf(generated_instances_s1, tokenizer, model)
        embedding2 = get_embedding_hf(instances_s2, tokenizer, model)
        similarity = cosine_similarity(
            embedding1.reshape(1, -1), embedding2.reshape(1, -1)
        )[0][0]
        return similarity

    elif model_name == "gpt":
        max_tokens = 2000
        if count_tokens(generated_instances_s1) > max_tokens:
            print(
                f"generated_instances_s1 dépasse {max_tokens} tokens. Tronquage en cours..."
            )
            generated_instances_s1 = truncate_text_to_limit(
                generated_instances_s1, max_tokens=max_tokens
            )
        if count_tokens(instances_s2) > max_tokens:
            print(f"instances_s2 dépasse {max_tokens} tokens. Tronquage en cours...")
            instances_s2 = truncate_text_to_limit(instances_s2, max_tokens=max_tokens)

        embedding1 = get_embedding_openai(generated_instances_s1)
        embedding2 = get_embedding_openai(instances_s2)
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        similarity_score_openai = cosine_similarity(embedding1, embedding2)[0][0]
        return similarity_score_openai
    return 0


def schema_inst_schema_ins_matcher(
    a_s1,
    attr_s1_ext,
    generated_instances_s1,
    generated_attrs_s2,
    instances_s2,
    model_name,
    df_DS1,
    df_DS2,
    fake_attr_s2,
):
    """
    Computes the similarity between the generated attributes and SC1 attributes.

    Args:
    generated_attributes (list): A list of generated attribute names from SC2.
    attr_s1 (list): A list of attribute names from SC1.
    model_name (str): The name of the model to use for generating embeddings (e.g., "bert-base-uncased").

    Returns:
    float: The similarity score between the generated attributes and SC1 attributes.
    """

    attr_s1 = " ".join([a_s1] + [attr_s1_ext]).replace("nan", "")
    print("generated_instances_s1 = ", generated_instances_s1)
    generated_instances_s1 = " ".join(map(str, generated_instances_s1)).replace(
        "nan", ""
    )
    S1 = attr_s1 + " " + generated_instances_s1
    print("generated_attrs_s2 = ", generated_attrs_s2)
    print(" ".join(generated_attrs_s2).replace("nan", ""))
    generated_attrs_s2_combined = (
        " ".join(generated_attrs_s2).replace("nan", "") if generated_attrs_s2 else ""
    )
    instances_s2 = " ".join(map(str, instances_s2)).replace("nan", "")
    S2 = generated_attrs_s2_combined + " " + instances_s2

    # Use a model to calculate embeddings and similarity
    if model_name in models_transformers:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        embedding1 = get_embedding_hf(S1, tokenizer, model)
        embedding2 = get_embedding_hf(S2, tokenizer, model)
        similarity = cosine_similarity(
            embedding1.reshape(1, -1), embedding2.reshape(1, -1)
        )[0][0]
    elif model_name == "gpt":
        max_tokens = 2000
        if count_tokens(S1) > max_tokens:
            print(f"S1 dépasse {max_tokens} tokens. Tronquage en cours...")
            S1 = truncate_text_to_limit(S1, max_tokens=max_tokens)
        if count_tokens(S2) > max_tokens:
            print(f"S2 dépasse {max_tokens} tokens. Tronquage en cours...")
            S2 = truncate_text_to_limit(S2, max_tokens=max_tokens)
        embedding1 = get_embedding_openai(S1)
        embedding2 = get_embedding_openai(S2)

        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        similarity = cosine_similarity(embedding1, embedding2)[0][0]

    if model_name != "gpt":
        df_DS1[a_s1] = embedding1
        df_DS2[fake_attr_s2] = embedding2
    else:
        df_DS1[a_s1] = embedding1[0]
        df_DS2[fake_attr_s2] = embedding2[0]
    return similarity, df_DS1, df_DS2
