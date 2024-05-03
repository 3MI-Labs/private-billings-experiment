# Private Billings experiment
Experiment code for the Private Billings project

# Installation
Installation involves the following steps:
1. Install OpenFHE-development, following its [installation procedure](https://openfhe-development.readthedocs.io/en/latest/sphinx_rsts/intro/installation/installation.html).

2. Install OpenFHE-python, following its [installation procedure](https://github.com/openfheorg/openfhe-python/tree/main?tab=readme-ov-file#linux).
Afterwards, make sure to add the installation file to your PYTHONPATH.
```sh
export PYTHONPATH=/path/to/OPENFHE_so_files:$PYTHONPATH
```

3. (recommended) Setup a virtual environment.
```
python3 -m venv .env
```

4. Install the private billings dependency
```sh
git clone git@github.com:3MI-Labs/private-billings-experiment.git --include-submodules
python3 -m pip install -e deps/private-billings
```