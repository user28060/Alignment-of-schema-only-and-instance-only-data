import ast
import json
import os

import requests

from schema_instance.schema_instance_llama.utils import (
    is_safe_code,
    make_valid_identifier,
    open_or_generate_with_best_option,
    save_auxiliary_informations,
)

url = "http://localhost:11434/api/chat"


def llama3(prompt):
    data = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Always ensure your responses are accurate, \
                complete, and strictly adhere to the query's requirements. Do not include None values or [] \
                in your output under any circumstances. \
                Be concise and precise, providing only the necessary information to fully address the query.",
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=data)
    return_result = str(response.json()["message"]["content"])

    return return_result


def get_auxiliary_informations(
    type_a_s1,
    name_s1,
    attributes_s1,
    fake_attributes_s2,
    instances_s2,
    types2,
    name_s2,
    categorie_dataset_name,
    path,
):
    print("path: ", path)
    # Initialiser les variables
    generated_instances_s1 = {}
    extended_sc1 = {}
    generated_attribute_s2 = {}

    if categorie_dataset_name == "Magellan":
        categorie_dataset_name = name_s1
    for i, a_s1 in enumerate(attributes_s1):
        # Définir les chemins avec et sans "best"
        generated_instance_path = os.path.join(
            path,
            "generated_instances",
            f"{categorie_dataset_name}_generated_instances_{a_s1}.json",
        )
        print("generated_instance_path", generated_instance_path)
        best_generated_instance_path = os.path.join(
            path,
            "best/generated_instances",
            f"{categorie_dataset_name}_generated_instances_{a_s1}.json",
        )

        extended_attribute_path = os.path.join(
            path,
            "extanded_attributes",
            f"{categorie_dataset_name}_extended_{a_s1}.json",
        )
        best_extended_attribute_path = os.path.join(
            path,
            "best/extanded_attributes",
            f"{categorie_dataset_name}_extended_{a_s1}.json",
        )

        # Ouvrir/générer les fichiers pour generated_instances_s1
        generated_instances_s1[a_s1], exist_ins_s2 = open_or_generate_with_best_option(
            best_generated_instance_path,
            generated_instance_path,
            generate_missing_instances,
            a_s1,
            type_a_s1[i],
            name_s1,
        )

        # Ouvrir/générer les fichiers pour extended_sc1
        extended_sc1[a_s1], exist_sc1_a_s1 = open_or_generate_with_best_option(
            best_extended_attribute_path,
            extended_attribute_path,
            generate_extended_attribute,
            a_s1,
            type_a_s1[i],
            name_s1,
        )
    for idx, (type_a_s2, ins_s1) in enumerate(zip(types2, instances_s2)):
        # Définir les chemins avec et sans "best"
        generated_attribute_s2_path = os.path.join(
            path,
            "generated_attributes",
            f"{categorie_dataset_name}_{name_s2}_generated_attribute_s2_{fake_attributes_s2[idx]}.json",
        )
        best_generated_attribute_s2_path = os.path.join(
            path,
            "best/generated_attributes",
            f"{categorie_dataset_name}_{name_s2}_generated_attribute_s2_{fake_attributes_s2[idx]}.json",
        )

        # Ouvrir/générer les fichiers pour generated_attribute_s2
        generated_attribute_s2[fake_attributes_s2[idx]], exist_a_s2 = (
            open_or_generate_with_best_option(
                best_generated_attribute_s2_path,
                generated_attribute_s2_path,
                generate_missing_attributes,
                ins_s1,
                type_a_s2,
                name_s2,
            )
        )

    assert len(generated_attribute_s2) == len(
        fake_attributes_s2
    ), "generated_attributes_s2 should have length equal to len(fake_attributes_s2)"
    assert len(generated_instances_s1) == len(
        attributes_s1
    ), "generated_instances_s1 should have length equal to len(attributes_s1)"
    assert len(extended_sc1) == len(
        attributes_s1
    ), "extended_sc1 should have length equal to len(attributes_s1)"
    return extended_sc1, generated_attribute_s2, generated_instances_s1


def save_auxiliary_informations(
    extended_sc1, generated_attributes_s2, generated_instances_s1, name_s1, path
):
    if extended_sc1 is not None or extended_sc1 != []:
        with open(
            os.path.join(
                path, "extanded_attributes", str(name_s1) + "_extended_sc1.json"
            ),
            "w",
        ) as f:
            json.dump(extended_sc1, f)

    if generated_attributes_s2 is not None or generated_attributes_s2 != []:
        with open(
            os.path.join(
                path,
                "generated_attributes",
                str(name_s1) + "_generated_attributes_s2.json",
            ),
            "w",
        ) as f:
            json.dump(generated_attributes_s2, f)
    if generated_instances_s1 is not None or generated_instances_s1 != []:
        with open(
            os.path.join(
                path,
                "generated_instances",
                str(name_s1) + "_generated_instances_s1.json",
            ),
            "w",
        ) as f:
            json.dump(generated_instances_s1, f)


def generate_auxiliary_informations(
    type_a_s1, name_s1, attributes_s1, instances_s2, types2, name_s2, path
):
    extended_sc1 = generate_extended_information_s1(type_a_s1, name_s1, attributes_s1)
    generated_attributes_s2 = generate_attributes_s2(types2, name_s2, instances_s2)
    generated_instances_s1 = generate_instances_s1(attributes_s1, type_a_s1, name_s1)
    if extended_sc1 is not None:
        extended_sc1 = generate_extended_information_s1(
            type_a_s1, name_s1, attributes_s1
        )

    if generated_attributes_s2 is not None:
        generated_attributes_s2 = generate_attributes_s2(types2, name_s2, instances_s2)

    if generated_instances_s1 is not None:
        generated_instances_s1 = generate_instances_s1(
            attributes_s1, type_a_s1, name_s1
        )
    save_auxiliary_informations(
        extended_sc1, generated_attributes_s2, generated_instances_s1, name_s1, path
    )
    return extended_sc1, generated_attributes_s2, generated_instances_s1


def process_extracted_instances(extracted_instances, a_s1):
    # Ensure brackets are balanced
    if extracted_instances.count("[") > extracted_instances.count("]"):
        extracted_instances += "]" * (
            extracted_instances.count("[") - extracted_instances.count("]")
        )
    elif extracted_instances.count("]") > extracted_instances.count("["):
        extracted_instances = (
            "[" * (extracted_instances.count("]") - extracted_instances.count("["))
            + extracted_instances
        )

    # Ensure elements are quoted properly
    try:
        # Strip brackets and add quotes around elements
        extracted_instances = extracted_instances.strip("[]")  # Remove outer brackets
        fixed_instances = "[{}]".format(
            ", ".join(f'"{item.strip()}"' for item in extracted_instances.split(","))
        )

        # Safely evaluate the fixed string as a Python list
        instances = ast.literal_eval(fixed_instances)
        if not isinstance(instances, list):
            raise ValueError("Parsed result is not a list.")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing instances: {e}")
        return a_s1  # Fallback if parsing fails

    return instances


def generate_missing_instances(a_s1, type_a_s1, name_s1):
    # Preprocess the data to ensure consistency

    # Prepare the prompt with a list of lists format requirement
    prompt = f"In a dataset named {name_s1}, based on the domain {name_s1}, the attribute {a_s1} \
    is of type {type_a_s1}. Generate a list of representative and relevant instances for this attribute. \
    These instances should accurately reflect the specified domain and adhere to the data type. Return only \
    a list in the format [instance1, instance2, ...], with no comments or empty values. Ensure the list is \
    properly closed with brackets."

    extracted_instances = llama3(prompt)
    processed_instances = process_extracted_instances(extracted_instances, a_s1)

    return processed_instances


def generate_extended_attribute(a_s1, type_a_s1, name_s1):
    # Messages pour l'API OpenAI avec une requête reformulée
    prompt = f"Enrich the a_s1 '{a_s1}' of type {type_a_s1} in the context of {name_s1} data. Provide detailed synonyms, related a_s1s, and multiple contextual examples where this a_s1 could be used. Also, give potential instances_s2 of how this a_s1 might appear in datasets, along with a deep explanation of its meaning, usage, and how it could match with different potential values in real-world data scenarios."

    # Extraction et transformation de la réponse en listes de synonymes, instances_s2 et exemples
    response_text = llama3(prompt).strip().replace("*", "")
    synonyms, instances_s2, examples = extract_synonyms_instances_s2_examples(
        response_text
    )

    # Retourner les résultats sous forme de texte lisible
    return ", ".join(synonyms) + ", ".join(examples) + ", ".join(instances_s2)


def generate_missing_attributes(ins_s2, type_a_s2, name_s2):
    # Preprocess the data to ensure consistency

    prompt = f"""
    Given the following values and types from the dataset named "{name_s2}":
    - Values: {ins_s2}
    - Type: {type_a_s2}
    Provide a list of possible attribute names.
    The list should include multiple attribute name options that are meaningful and represent the information accurately based on the given values and type, do not return empty lists!.
    The output should strictly be in the format of a list, which includes attribute names, like this:
    [attribute1, attribute2, ...]
    Only return the list as the output, without any additional comments or explanations.
    """
    # Extract the response text
    extracted_attributes = llama3(prompt).strip()

    # Clean up the response
    extracted_attributes = extracted_attributes.replace("\n", "").replace("...", "")

    # Ensure brackets are balanced
    if extracted_attributes.count("[") != extracted_attributes.count("]"):
        extracted_attributes += "]" * (
            extracted_attributes.count("[") - extracted_attributes.count("]")
        )

    # Safely evaluate the extracted string as Python lists
    try:
        attributes = ast.literal_eval(extracted_attributes)
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing attributes: {e}")
        return None  # Return None or handle as needed

    # Remove brackets from values (assuming you want to process the values in some way)
    attributes = remove_brackets_from_values(attributes)
    if extracted_attributes is None:
        extracted_attributes = ins_s2
    return attributes


def generate_instances_s1(attributes_s1, types1, name_s1):
    return [
        list(generate_missing_instances(a_s1, type_a_s1, name_s1))
        for type_a_s1, a_s1 in zip(types1, attributes_s1)
    ]


def generate_extended_information_s1(types1, name_s1, attributes_s1):
    return [
        list(generate_extended_attribute(a_s1, type_a_s1, name_s1))
        for a_s1, type_a_s1 in zip(attributes_s1, types1)
    ]


def generate_attributes_s2(types2, name_s2, instances_s2):

    return [
        list(generate_missing_attributes(ins_s2, type_a_s2, name_s2))
        for type_a_s2, ins_s2 in zip(types2, instances_s2)
    ]


def remove_brackets_from_values(data):
    updated_data = []
    for sublist in data:
        # If the last element is a list (the values part), convert it to comma-separated values
        if isinstance(sublist[-1], list):
            # Append all elements except the last one, then append the values without brackets
            updated_data.append(sublist[:-1] + sublist[-1])
        else:
            updated_data.append(sublist)
    return updated_data


def remove_brackets_from_values_att(data):
    updated_data = []

    # If the last element is a list (the values part), convert it to comma-separated values
    if isinstance(data[-1], list):
        # Append all elements except the last one, then append the values without brackets
        updated_data.append(data[:-1] + data[-1])
    else:
        updated_data.append(data)
    return updated_data[0]


def extract_synonyms_instances_s2_examples(text):
    # Diviser la réponse en parties basées sur des mots-clés comme "Synonyms", "instances_s2", "Examples"
    lines = text.split("\n")
    synonyms = []
    instances_s2 = []
    examples = []

    # Extraire chaque section à partir de la réponse
    current_section = None
    for line in lines:
        line = line.strip()
        if "Synonyms:" in line:
            current_section = "synonyms"
        elif "instances_s2:" in line:
            current_section = "instances_s2"
        elif "Examples:" in line:
            current_section = "examples"
        elif current_section == "synonyms" and line:
            synonyms.append(
                line.lstrip("0123456789. ")
                .strip("- ")
                .strip()
                .replace("**Related a_s1s:**,", " ")
            )
        elif current_section == "instances_s2" and line:
            instances_s2.append(
                line.lstrip("0123456789. ")
                .strip("- ")
                .strip()
                .replace("**Related a_s1s:**,", " ")
            )
        elif current_section == "examples" and line:
            examples.append(
                line.lstrip("0123456789. ")
                .strip("- ")
                .strip()
                .replace("**Related a_s1s:**,", " ")
            )

    return synonyms, instances_s2, examples


def generate_strict_rules_for_attribute(attribute_name, dataset_name, data_type):
    # Formulate the prompt
    prompt = f"""Generate strict and clear validation rules for the attribute {attribute_name} \
        from the dataset {dataset_name} with the data type {data_type}. Exclude any rules related \
            to non-emptiness. Provide the output as a Python list, where each rule is a string. \
                Only output the Python list without any additional information or formatting.
    """

    generated_rules = llama3(prompt).strip()

    return generated_rules


def generate_validation_function(attribute_name, category_name, data_type):
    # Get the rules from the previous function
    rules = generate_strict_rules_for_attribute(
        attribute_name, category_name, data_type
    )
    # Create the prompt to generate the validation function
    prompt = f"Create a Python function named \
            validate_{make_valid_identifier(attribute_name)}_{make_valid_identifier(category_name)} \
            that validates the following rules: {rules}. The function should take a list of values as input. \
            It should use only basic functions, avoid eval() and functions like bit_length, \
                and ensure no errors such as AttributeError or SyntaxError. The function must \
                    not include data[{attribute_name}]. The function should return True if all \
                        values validate the rules; otherwise, return False. Output the Python function \
                            as plain code, without any backticks or formatting."

    generated_code = llama3(prompt).strip()
    if is_safe_code(generated_code):
        return generated_code
    else:
        return generate_validation_function(attribute_name, category_name, data_type)


def possibility_gen_rules_function(attribute_name, category_name, data_type):
    prompt = (
        f"If in this function {generate_validation_function(attribute_name, category_name, data_type)}"
        "we check using simple common rules like non-null, correct type, length checks, or logical computation such as a regular expression for format,or generic rule that works every time, respond with 'True'. "
        "else return 'False'. "
        "Do not generate any list or code, only respond with 'True' or 'False'."
    )
    # Extract the response
    result = llama3(prompt).strip()
    return result
