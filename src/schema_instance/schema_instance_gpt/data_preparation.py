import numpy as np
import pandas as pd


def convert_percentage(val):
    val = val.strip()  # Supprime les espaces autour
    if val.endswith("%"):
        try:
            return float(val.strip("%"))  # Supprime le % et convertit en float
        except ValueError:
            return np.nan  # Si la conversion échoue, retourne NaN
    elif val == "-":
        return np.nan  # Convertit '-' en NaN
    return val  # Retourne la valeur inchangée si ce n'est pas un pourcentage


def preprocess_data(values):
    preprocessed_values = []
    for value_set in values:
        cleaned_value_set = []
        for value in value_set:
            if (isinstance(value, float) and np.isnan(value)) or (
                isinstance(value, str) and value.lower() == "nan"
            ):
                continue  # Skip NaN or 'nan' values
            elif isinstance(value, (int, float)):
                cleaned_value_set.append(value)
            else:
                cleaned_value_set.append(str(value).strip())
        preprocessed_values.append(cleaned_value_set)
    return preprocessed_values


def prepare_data(path_csv_s1, path_csv_s2):
    print("path_csv_s1", path_csv_s1)
    print("path_csv_i2", path_csv_s2)
    path_type1 = path_csv_s1.replace(".csv", ".json")
    path_type2 = path_csv_s2.replace(".csv", ".json")
    mapping_path = path_csv_s2.replace("_target.csv", "_mapping.json")
    name_s1 = path_csv_s2.split("/")[-2]
    name_s2 = path_csv_s2.split("/")[-2]
    df1 = pd.read_csv(path_csv_s1)
    attributes_s1 = df1.columns.tolist()
    types1 = pd.read_json(path_type1).T.type.tolist()

    df2 = pd.read_csv(path_csv_s2)
    df2 = df2.fillna("")
    types2 = pd.read_json(path_type2).T.type.tolist()
    instances_s2 = preprocess_data(df2.T.values.tolist())
    fake_attributes_s2 = df2.columns.tolist()
    try:
        df2["col_4"] = df2["col_4"].apply(convert_percentage)
    except BaseException:
        pass

    return (
        name_s1,
        name_s2,
        path_csv_s1,
        path_csv_s2,
        mapping_path,
        attributes_s1,
        instances_s2,
        fake_attributes_s2,
        types1,
        types2,
    )
