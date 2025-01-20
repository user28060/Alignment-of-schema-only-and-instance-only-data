# Alignment-of-schema-only-and-instance-only-data

[![version](https://img.shields.io/github/v/release/okp4/template-python?style=for-the-badge&logo=github)](https://github.com/okp4/template-python/releases)
[![lint](https://img.shields.io/github/actions/workflow/status/okp4/template-python/lint.yml?label=lint&style=for-the-badge&logo=github)](https://github.com/okp4/template-python/actions/workflows/lint.yml)
[![build](https://img.shields.io/github/actions/workflow/status/okp4/template-python/build.yml?label=build&style=for-the-badge&logo=github)](https://github.com/okp4/template-python/actions/workflows/build.yml)
[![test](https://img.shields.io/github/actions/workflow/status/okp4/template-python/test.yml?label=test&style=for-the-badge&logo=github)](https://github.com/okp4/template-python/actions/workflows/test.yml)
[![codecov](https://img.shields.io/codecov/c/github/okp4/template-python?style=for-the-badge&token=G5OBC2RQKX&logo=codecov)](https://codecov.io/gh/okp4/template-python)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge&logo=conventionalcommits)](https://conventionalcommits.org)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg?style=for-the-badge)](https://github.com/semantic-release/semantic-release)
[![contributor covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg?style=for-the-badge)](https://github.com/okp4/.github/blob/main/CODE_OF_CONDUCT.md)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg?style=for-the-badge)](https://opensource.org/licenses/BSD-3-Clause)

## Purpose & Philosophy

This repository holds the code and results for the paper "Alignment of schema-only and instance-only data sources using large language models"

### Abstract

Data matching is a persistent challenge in heterogeneous data integration. Traditional data matching methods, relying on schema-based, instance-based, or hybrid approaches, often fall short when aligning disparate data from schema-only with instance-only sources. To address this problem of aligning disparate sources, we present an innovative data matching framework that enables the matching of one data source, where only schema-related information is available, with another data source, where only instance-related information is available. The strength of our framework lies in its ability to combine outputs from multiple Schema-Instances matchers, generating auxiliary information to enhance the alignment between disparate data structures. Our framework is validated using the Valentine Benchmark through extensive experiments. These findings underscore the potential of our approach to advance the integration of diverse data sources.

Keywords: Data matching · Disparate Data Source Structures · Aux-
iliary Information Generation · Matcher Combination.

### Summary of the experimental evaluation

***Technical environment***

We deploy our approach and its variations using PyTorch version 1.6.0 with CPU support. The experiments were conducted on a system equipped with an Intel Core i7-10750H processor, featuring 6 cores running at 2.6 GHz (up to 5.0 GHz with Turbo Boost). The system has 16 GB of RAM, which provides sufficient memory for the experiments.

The framework was evaluated by testing various models for generating auxiliary information and embeddings. For generating auxiliary information, two models, GPT-3.5 and Llama-3.2, were used. Additionally, seven different embedding models were tested across schema, instance, and hybrid matchers, including BERT, RoBERTa, DistilBERT, ALBERT, Bart, the Sentence-transformer model all-MiniLM-L6-v2, and GPT-3.5. The performance of these combinations was assessed using the F1 score and NDCG metrics.

***Datasets***

In our experiments, we exploited the potential of five dataset categories, as described in the ["Valentine"](https://zenodo.org/records/5084605). These collections range from matching simple structured datasets to more complex configurations.

## Results

**RQ1 - Effectiveness**
This question aimed to evaluate the framework’s effectiveness in terms of precision (F1 score) and ranking quality (NDCG).

**Key Findings:**

GPT-3.5 is the best choice for auxiliary information generation, producing high-quality inputs that enhance embedding performance. GPT embeddings consistently outperform other models across all tasks, delivering reliable and high-quality results with lower variability. While simpler Unionable relations achieve the best outcomes, the robustness of GPT embeddings and GPT-3.5’s generation capabilities ensure competitive performance even in more complex relations requiring semantic reasoning.

**RQ2 - Efficiency**
This question assessed the execution time of the framework across datasets and embedding models.

**Key Findings:**

Execution times are affected by the dataset source, embedding model, and dataset characteristics. Llama-3.2 is slightly faster overall, but GPT-3.5 adapts better to sources with more attributes or complex data, like Wikidata. The number of attributes is the main factor influencing execution time, as auxiliary information and embeddings must be generated for each attribute-instance pair. This explains why datasets with fewer rows but many attributes, like \\textit{fodors_zagats}, require as much time as larger datasets.

Lightweight models like MiniLM for emebddings generation are more efficient but are less reliable for complex datasets. GPT-3.5 for generating auxiliary informations, while slightly slower, handles tasks with higher complexity or more attributes better, making it the preferred choice for tasks requiring effectiveness and stability.

**RQ3 - Noise Sensitivity**
This question explored the robustness of the framework against varying levels of attribute noise.

Key Findings:

The solution's robustness across different noise levels highlights its effectiveness in handling schema-only and instance-only data sources. The minimal impact of schema-level noise, such as typographical or structural changes, is attributed to GPT’s data enrichment process, which contextualizes noise and enhances comprehension. This robustness ensures high performance in both classification and ranking tasks, making the solution well-suited for real-world noisy datasets.

**RQ4 - Ablation Study**
This question examined the impact of removing individual matchers from the framework on performance metrics (F1 score and NDCG).

Key Findings:

The findings underscore the critical role of Instances Matcher and Schema-Instances matcher in achieving optimal performance. These matchers demonstrated significant contributions not only statistically but also practically, enhancing precision but decreases ranking quality. The observed reduction in AIC suggests improved model parsimony and efficiency, while the slight improvements in F1 Score (+0.004) emphasize the impact of small optimizations on overall performance.

The results also highlight the potential to further improve performance by excluding less impactful matchers, such as Rule Matcher and Schema Matcher, which may detract from the overall quality. This suggests that specific matcher combinations may perform better for certain dataset characteristics, presenting an opportunity to develop recommendations tailored to dataset attributes. These findings align with the hypothesis that matchers interact synergistically, emphasizing the need to adapt matcher combinations dynamically for different data scenarios.

## Conclusion

This repository addresses the challenge of aligning disparate data sources, where one provides only schema information and the other only Instance data. It introduces a novel data matching framework, evaluated through experiments on effectiveness, efficiency, noise resilience, and matcher ablation. The framework leverages Schema-Instance matchers to generate auxiliary information and enable alignment.

The experiments, based on the Valentine Benchmark, identified the GPT-3.5 model as the best-performing for generating auxiliary information and embeddings, achieving optimal results in terms of F1 Score and NDCG. The ablation study further highlighted the critical roles of the Instances Matcher, Schema-Instances Matcher, and Type Matcher. These components worked synergistically to enhance effectiveness and ranking quality.

Efficiency analysis revealed the significant impact of dataset characteristics, such as the number of rows and attributes, on execution time, offering actionable insights for optimizing large-scale data matching tasks.

All results, detailed analyses, and accompanying figures are available in the respective folders for each research question.

This way, the template promotes:

- the use of [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/), [semantic versionning](https://semver.org/) and [semantic releasing](https://github.com/cycjimmy/semantic-release-action) which automates the whole package release workflow including: determining the next version number, generating the release notes, and publishing the artifacts (project tarball, docker images, etc.)
- a uniform way for managing the project lifecycle (dependencies management, building, testing)
- KISS principles: simple for developers
- a consistent coding style

## System requirements

### Python

The repository targets python `3.10` and higher.

### GPT-3.5

- **API Key**: Obtain from [OpenAI](https://platform.openai.com/docs/api-reference/introduction).

### Llama-3.2

- iInstall Ollama from [Ollama](https://ollama.com/download)
- API available at `http://localhost:11434/api/chat`.

______________________________________________________________________

### 2. Example of Usage

#### GPT-3.5 Example

```python
import openai
openai.api_key = "your-api-key"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)
print(response["choices"][0]["message"]["content"])
# Paris
```

#### Llama-3.2 Example

```sh
ollama run llama3.2
```

```python
import requests

llama_api_url = "http://localhost:11434/api/chat"

data = {
    "model": "llama3.2",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {"role": "user", "content": "What is the capital of France?"},
    ],
    "stream": False,
}

headers = {"Content-Type": "application/json"}

response = requests.post(llama_api_url, headers=headers, json=data)
return_result = str(response.json()["message"]["content"])

print(return_result)
# The capital of France is Paris.'
```

______________________________________________________________________

## 4. Resources

- [OpenAI API Docs](https://platform.openai.com/docs/api-reference/introduction)
- [Llama-3.2 Documentation](https://ollama.com/library/llama3.2)

### Poetry

The repository uses [Poetry](https://python-poetry.org) as python packaging and dependency management. Be sure to have it properly installed before.

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
Or, 
```sh
curl -sSL https://install.python-poetry.org | python3 -
```

### Docker

You can follow the link below on how to install and configure **Docker** on your local machine:

- [Docker Install Documentation](https://docs.docker.com/install/)

## What's included

This template provides the following:

- [poetry](https://python-poetry.org) for dependency management.
- [flake8](https://flake8.pycqa.org) for linting python code.
- [mypy](http://mypy-lang.org/) for static type checks.
- [pytest](https://docs.pytest.org) for unit testing.
- [click](https://palletsprojects.com/p/click/) to easily setup your project commands

The project is also configured to enforce code quality by declaring some CI workflows:

- conventional commits
- lint
- unit test
- semantic release

## Everyday activity

### Build

Project is built by [poetry](https://python-poetry.org).

```sh
poetry install
```

### Usage

```sh
poetry run schema-instance matching --help
```

Will give something like

```console
Usage: schema-instance matching [OPTIONS]

  Generic matching function.

Options:
  -s1, --input-S1 TEXT            path to text file  [required]
  -i2, --input-I2 TEXT            path to text file  [required]
  --generative-model [gpt|llama]  Choose the generative model to use: 'gpt' or
                                  'llama'.
  --embedding-model [...]         Choose an embedding model from the predefined
                                  list.
  -o, --output TEXT               output directory where json file will be
                                  written  [default: .]
  -f, --force                     overwrite existing file
  --dry-run                       passthrough, will not write anything
  --help                          Show this message and exit.
```

Example:

```sh
poetry run schema-instance matching -s1 tests/inputs/datasets_instances/Magellan/Unionable/amazon_google_exp/amazon_google_exp_source.csv -i2 tests/inputs/datasets_instances/Magellan/Unionable/amazon_google_exp/amazon_google_exp_target.csv -o ./tests/outputs/results_dataframes -GenMod gpt -f
```
The pair matches outputs of the example should be in the file "tests/outputs/bert-base-uncased/matches/amazon_google_exp.json"



### Lint

> ⚠️ Be sure to write code compliant with linters or else you'll be rejected by the CI.

**Code linting** is performed by [flake8](https://flake8.pycqa.org).

```sh
poetry run flake8 --count --show-source --statistics
```

**Static type check** is performed by [mypy](http://mypy-lang.org/).

```sh
poetry run mypy .
```

To improve code quality, we use other linters in our workflows, if you don't want to be rejected by the CI,
please check these additional linters.

**Markdown linting** is performed by [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli).

```sh
markdownlint "**/*.md"
```

**Docker linting** is performed [hadolint](https://github.com/hadolint/hadolint).

```sh
hadolint Dockerfile
```

### Unit Test

> ⚠️ Be sure to write tests that succeed or else you'll be rejected by the CI.

Unit tests are performed by the [pytest](https://docs.pytest.org) testing framework.

```sh
poetry run pytest -v
```

### Build & run docker image (locally)

Build a local docker image using the following command line:

```sh
docker build -t schema-instance.
```

Once built, you can run the container locally with the following command line:

```sh
docker run -ti --rm schema-instance
```
