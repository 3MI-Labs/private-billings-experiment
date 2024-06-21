# Private Billings experiment
Experiment code for the [Private Billings](https://github.com/3MI-Labs/private-billings) library.

# Installation
Installation involves the following steps:
1. Clone this repository and its submodules
```sh
git clone git@github.com:3MI-Labs/private-billings-experiment.git --include-submodules
```

2. Install OpenFHE-development, following its [installation procedure](https://openfhe-development.readthedocs.io/en/latest/sphinx_rsts/intro/installation/installation.html).

3. Install OpenFHE-python, following its [installation procedure](https://github.com/openfheorg/openfhe-python/tree/main?tab=readme-ov-file#linux).
We recommend installing at commit `87700c2c250ff39eaaa5cbe4daed3e5cb5d9b726`; later installations introduce an obscure bug.
Afterwards, make sure to add the installation file to your PYTHONPATH.
```sh
export PYTHONPATH=/path/to/OPENFHE_so_files:$PYTHONPATH
```

4. (recommended) Setup a virtual environment
```sh
python3 -m venv .env
```

5. Install the dependencies
```sh
pip install -r requirements.txt
```

6. Install the private billings dependency
```sh
python3 -m pip install -e deps/private-billings
```

At this point you should be able to launch a python shell and utilize the `private_billings` library.
To verify this, open a shell and simply
```python
import private_billings
```

7. Install the [`private-billings-data-generation`](https://github.com/3MI-Labs/private-billings-data-generation) repository.
This repository can be used to generate the data required for this experiment.
The generated data should be placed in the `data/` folder.

More details in the installation procedure can be derived from the [Dockerfile](docker/Dockerfile).
