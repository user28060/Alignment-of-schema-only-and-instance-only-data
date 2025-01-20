import json
import logging
import os
import time

import click
import pandas as pd

import schema_instance.__init__ as init
from schema_instance.schema_instance_gpt.call_schema_instance import process_file_gpt
from schema_instance.schema_instance_llama.call_schema_instance import (
    process_file_llama,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    level=logging.INFO,
)


def validate_dir_path(ctx, param, value):
    if not os.path.isdir(value):
        raise click.BadParameter("path must point to an existing directory")
    return value


def validate_file_path(ctx, param, value):
    if not os.path.isfile(value):
        raise click.BadParameter("path must point to an existing file")
    return value


@click.group
def cli():
    """Represents the root cli function"""


@cli.command
def version():
    """Represents cli 'version' command"""
    click.echo(init.__version__)


@cli.command()
@click.option(
    "-s1",
    "--input-S1",
    "input_file_s1",
    type=str,
    callback=validate_file_path,
    required=True,
    help="path to text file",
)
@click.option(
    "-i2",
    "--input-I2",
    "input_file_i2",
    type=str,
    callback=validate_file_path,
    required=True,
    help="path to text file",
)
@click.option(
    "-GenMod",
    "--generative-model",
    "generative_model",
    type=click.Choice(["gpt", "llama"], case_sensitive=False),
    default="gpt",
    help="Choose the generative model to use: 'gpt' or 'llama'.",
)
@click.option(
    "-EmbMod",
    "--embedding-model",
    "embedding_model",
    type=click.Choice(
        [
            "bert-base-uncased",
            "distilbert-base-uncased",
            "sentence-transformers/all-MiniLM-L6-v2",
            "albert-base-v2",
            "facebook/bart-base",
            "gpt",
            "roberta-base",
        ],
        case_sensitive=False,
    ),
    default="bert-base-uncased",
    help="Choose an embedding model from the predefined list.",
)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=str,
    callback=validate_dir_path,
    default=".",
    show_default=True,
    help="output directory where json file will be written",
)
@click.option(
    "-f",
    "--force",
    "overwrite",
    type=bool,
    is_flag=True,
    default=False,
    help="overwrite existing file",
)
@click.option(
    "--dry-run",
    "dry_run",
    type=bool,
    is_flag=True,
    default=False,
    help="passthrough, will not write anything",
)
def matching(
    input_file_s1: str,
    input_file_i2: str,
    generative_model,
    embedding_model,
    output_dir: str,
    overwrite: bool = False,
    dry_run: bool = False,
):
    """Generic matching function."""

    os.makedirs(output_dir, exist_ok=True)
    dataset_name = os.path.basename(input_file_s1).split(".")[0]
    output_file = os.path.join(output_dir, dataset_name, ".csv")

    df = pd.DataFrame(
        columns=[
            "Dataset",
            "generative_model",
            "embedding_model",
            "F1_Score",
            "Precision",
            "Recall",
            "Execution_Time",
        ]
    )
    print(f"Created a new DataFrame with columns {df.columns.tolist()}")

    start_time = time.time()

    if generative_model == "gpt":
        key_api_gpt = input("Please enter your GPT-3.5 API key to proceed: ")
        df = process_file_gpt(
            input_file_s1, input_file_i2, embedding_model, df, key_api_gpt
        )
    else:
        print(
            "Note: To use Llama-3.2, you must install it locally. Visit https://ollama.com/library/llama3.2 for more details.\n"
            "Ensure that your system meets the requirements:\n"
            " - Python version: 3.10 or higher\n"
        )
        df = process_file_llama(input_file_s1, input_file_i2, embedding_model, df)

    end_time = time.time()
    print(f"Processing completed in {end_time - start_time:.2f} seconds")
    dataset_name = os.path.basename(input_file_s1).split(".")[0]
    output_file = os.path.join(
        output_dir,
        generative_model + "_" + embedding_model + "_" + dataset_name + ".csv",
    )
    name = dataset_name.replace("_source", "")
    
    path= os.getcwd().split('/')
    i=path.index('Alignment-of-schema-only-and-instance-only-data')
    folder_path= "/".join(path[:i+1])
    path_file = f"/tests/outputs/{embedding_model}/matches/{name}.json"
    path_matches = folder_path + path_file
    with open(path_matches, "r") as file:
        data = json.load(file)
        print(data)

    print(
        f'The pair matches outputs of the example should be in the file: "{output_file}"'
    )
    if not dry_run:
        if overwrite or not os.path.exists(output_file):
            logging.info(f"the csv with name {dataset_name} was saved succefully")
            df.to_csv(output_file, index=False)
        else:
            logging.error(f"the csv with name {dataset_name} is duplicated")
            raise ValueError(f"{dataset_name} already exists")


if __name__ == "__main__":
    cli()
