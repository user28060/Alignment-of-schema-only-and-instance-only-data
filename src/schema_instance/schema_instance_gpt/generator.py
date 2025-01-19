import ast
import os

import openai

from schema_instance.schema_instance_gpt.utils import (
    extract_dictionary_from_response,
    is_safe_code,
    make_valid_identifier,
    open_or_generate_with_best_option,
    save_auxiliary_informations,
)


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
    key_api_gpt,
):
    openai.api_key = key_api_gpt
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


def generate_auxiliary_informations(
    type_a_s1, name_s1, attributes_s1, instances_s2, types2, name_s2, path
):
    extended_sc1 = generate_extended_information_s1(type_a_s1, name_s1, attributes_s1)
    generated_attributes_s2 = generate_attributes_s2(types2, name_s2, instances_s2)
    generated_instances_s1 = generate_instances_s1(attributes_s1, type_a_s1, name_s1)
    save_auxiliary_informations(
        extended_sc1, generated_attributes_s2, generated_instances_s1, name_s1, path
    )
    return extended_sc1, generated_attributes_s2, generated_instances_s1


def generate_missing_instances(a_s1, type_a_s1, name_s1):
    # Preprocess the data to ensure consistency

    # Prepare the prompt with a list of lists format requirement
    prompt = f"""
    Given the following atributes and types from the dataset named "{name_s1}":
    - domain: {name_s1}
    - a_s1: {a_s1}
    - Type_a1: {type_a_s1}
    For The column/attribute {a_s1}, provide a list of possible instances/values.
    The list should include multiple instances/values  that are meaningful and represent the information accurately based on the given a_s1, Type_a1 and domain.
    The output should strictly be in the format of a list that represent instances/values for the attribute a_s1, like this:
    [instance1, instance2, ...]
    Only return the list as the output, without any additional comments or explanations. Please finish the list output and do close all the brackets, do not return empty list!.
    """

    # OpenAI API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    # Extract the response text
    extracted_instances = response["choices"][0]["message"]["content"].strip()
    # Clean up the response
    extracted_instances = extracted_instances.replace("\n", "").replace("...", "")

    # Ensure brackets are balanced
    if extracted_instances.count("[") != extracted_instances.count("]"):
        extracted_instances += "]" * (
            extracted_instances.count("[") - extracted_instances.count("]")
        )

    # Ensure brackets are balanced
    # Safely evaluate the extracted string as Python lists
    try:
        instances = ast.literal_eval(extracted_instances)
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing instances: {e}")
        return None  # Return None or handle as needed
    # Remove brackets from values (assuming you want to process the values in some way)
    instances = remove_brackets_from_values_att(instances)

    return instances


def generate_extended_attribute(a_s1, type_a_s1, name_s1):
    # Messages pour l'API OpenAI avec une requête reformulée
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides detailed semantic descriptions.",
        },
        {
            "role": "user",
            "content": f"Enrich the a_s1 '{a_s1}' of type {type_a_s1} in the context of {name_s1} data. Provide detailed synonyms, related a_s1s, and multiple contextual examples where this a_s1 could be used. Also, give potential instances_s2 of how this a_s1 might appear in datasets, along with a deep explanation of its meaning, usage, and how it could match with different potential values in real-world data scenarios.",
        },
    ]

    # Appel à l'API OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,  # Augmenté pour obtenir des réponses plus détaillées
        temperature=0.7,
    )

    # Extraction et transformation de la réponse en listes de synonymes, instances_s2 et exemples
    response_text = response.choices[0]["message"]["content"].strip()
    synonyms, instances_s2, examples = extract_synonyms_instances_s2_examples(
        response_text
    )

    # Retourner les résultats sous forme de texte lisible
    return ", ".join(synonyms) + ", ".join(examples)


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
    # OpenAI API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7,
    )

    # Extract the response text
    extracted_attributes = response["choices"][0]["message"]["content"].strip()

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
    prompt = (
        f"Generate strict, clear validation rules for the attribute '{attribute_name}' "
        "ignore the non-empty rule."
        f"from the dataset '{dataset_name}' with data type '{data_type}'. "
        f"Output the rules as a list in Python, with each rule as a string."
    )

    # Call OpenAI API with the generated prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates strict Python validation rules.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.3,  # Lower temperature for stricter outputs
    )

    # Extract the response
    generated_rules = response["choices"][0]["message"]["content"].strip()

    return generated_rules


def generate_validation_function(attribute_name, category_name, data_type):
    # Get the rules from the previous function
    rules = generate_strict_rules_for_attribute(
        attribute_name, category_name, data_type
    )
    # Create the prompt to generate the validation function
    prompt = (
        f"Create a Python function named `validate_{make_valid_identifier(attribute_name)}_{make_valid_identifier(category_name)}` that validates the following rules:\n{rules}. \n"
        "The function should take a **list** of values in the input. "
        " the functio should use only basic functions not AttributeError: 'float' object has no attribute 'bit_length'"
        " avoid functions with eval() and do not forget the imports packages"
        "theses functions will be used dynamically, so please be sure to make it functional without any errors"
        " please malke sure to not have SyntaxError: invalid syntax"
        "The function should return True if the `values` validates all the rules, otherwise return False.\n"
        "The function shouldnt contain data[{attribute_name}]"
        "Output the Python function without backticks or any markdown formatting, just plain Python code."
    )

    # Call OpenAI API to generate the validation function
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates Python code.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,  # A bit of flexibility in the response
    )

    # Extract the generated function code

    generated_code = response["choices"][0]["message"]["content"].strip()
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
    # Call the OpenAI API with the generated prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates Python code.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=50,  # Since we only need True/False, this is enough
        temperature=0.1,  # We want a dea_s1inistic response
    )

    # Extract the response
    result = response["choices"][0]["message"]["content"].strip()
    return result


def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.5,
    )
    return response["choices"][0]["message"]["content"].strip()


def match_schema_to_schema(attributes_s1, generated_attributes_s2):
    prompt = f"""
    I have two datasets and I need to match their schemas:
    1. **Schema (attributes) from Dataset 1**: {attributes_s1}
    2. **Schema (attributes) from Dataset 2**: {generated_attributes_s2}
    Please generate a Python dictionary where each key is an attribute from Dataset 1 (attributes_s1) 
    and the value is the corresponding best matching attribute or list of attributes from Dataset 2 (generated_attributes_s2). 
    Ensure that the keys come from Dataset 1 and the values come from Dataset 2.
    """
    # Get response from GPT
    response_text = get_gpt_response(prompt)

    # Extract and return the dictionary
    schema_match = extract_dictionary_from_response(response_text)
    # Ensure that all keys are from attributes_s1, even if no match is found
    for attr in attributes_s1:
        if attr not in schema_match:
            schema_match[attr] = None  # If no match, set as None

    return schema_match


def match_instance_to_instance(instances_s1, instances_s2):
    prompt = f"""
    
    I have two datasets and I need to match their instances:
    1. **Instances from Dataset 1**: {instances_s1}
    2. **Instances from Dataset 2**: {instances_s2}    
    Please generate a Python dictionary where each key is a key from Dataset 1 (instances_s1) 
    and the value is the corresponding matching instance or list of instances from Dataset 2 (instances_s2). 
    Ensure that the keys come from Dataset 1 and the values come from Dataset 2.
    
    """
    # Get response from GPT
    response_text = get_gpt_response(prompt)
    # Extract and return the dictionary
    instance_match = extract_dictionary_from_response(response_text)
    # Ensure that all keys are from instances_s1, even if no match is found
    for key in instances_s1.keys():
        if key not in instance_match:
            instance_match[key] = None  # If no match, set as None

    return instance_match


def match_schema_instance_to_schema_instance(
    attributes_s1, generated_attributes_s2, instances_s1, instances_s2
):
    prompt = f"""
    
    I have two datasets and I need to match their schema-instance pairs:
    1. **Schema (attributes) from Dataset 1**: {attributes_s1}
    2. **Schema (attributes) from Dataset 2**: {generated_attributes_s2}
    3. **Instances from Dataset 1**: {instances_s1}
    4. **Instances from Dataset 2**: {instances_s2}
    Please generate a Python dictionary where each key is an attribute from Dataset 1 (attributes_s1), 
    and the value is the corresponding match or matches from Dataset 2 (generated_attributes_s2), 
    ensuring that keys are strictly from Dataset 1 and values come from Dataset 2.
    
    """
    # Get the GPT response
    response_text = get_gpt_response(prompt)
    # Extract the dictionary from the GPT response
    schema_instance_match = extract_dictionary_from_response(response_text)
    # Ensure that all keys from attributes_s1 are included in the output dictionary
    for key in attributes_s1:
        if key not in schema_instance_match:
            schema_instance_match[key] = None  # If no match, set as None

    return schema_instance_match
