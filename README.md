Quantum XYZ
===========

<!-- [![DOI](https://zenodo.org/badge/598144740.svg)](https://zenodo.org/badge/latestdoi/598144740) -->
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/Nozidoali/quantum-xyz.git)
[![Python CI](https://github.com/Nozidoali/quantum-xyz/actions/workflows/python-checks.yaml/badge.svg)](https://github.com/Nozidoali/quantum-xyz/actions/workflows/python-checks.yaml)[![Documentation Status](https://readthedocs.org/projects/quantum-xyz/badge/?version=latest)](https://quantum-xyz.readthedocs.io/en/latest/?badge=latest)



XYZ is a Python package for quantum circuit synthesis. It provides several implementations for quantum circuit optimizations, such as exact CNOT synthesis. [Read full documentation](https://quantum-xyz.readthedocs.io/en/latest/)

## Example

```sh
pip install quantum-xyz
cd example
python synthesize_dicke.py
```

## Installation
 
1. Install poetry (`>=2.0.0`), see [official instruction](https://python-poetry.org/docs/)
2. Build dist locally by running `poetry build`
3. Setup the environment by running `poetry install`
4. Run example using `poetry run python example/synthesize_dicke.py`

## Quantum State Preparation Using an Exact CNOT Synthesis Formulation
See [xyz/algorithms/prepare_state](xyz/algorithms/prepare_state)

Reference:
```
    @article{wang2024quantum,
        title={Quantum State Preparation Using an Exact CNOT Synthesis Formulation},
        author={Wang, Hanyu and Tan, Bochen and Cong, Jason and De Micheli, Giovanni},
        journal={arXiv preprint arXiv:2401.01009},
        year={2024}
    }
```
