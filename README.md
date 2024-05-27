# planGPT -     Learning General Policies for Planning through GPT Models
This repository includes  the provided code for the paper ```Learning General Policies for Planning through GPT Models``` (https://openreview.net/pdf?id=yB8oafJ8bu). The code includes multiple scripts:
- [scripts/plan_generator.py](scripts/plans_generator.py): script to generate plans given a dataset of planning problems.
- [scripts/validator.ipynb](scripts/validator.ipynb): script to validate the generated plans.
- [scripts/solver_pddl.py](scripts/solver_pddl.py): script to generate a planGPT plan using as input a PDDL problem.
- [scripts/metric.py](scripts/metric.py): script inspired by VAL that given an initial state, goal state, plan and domain verifies if the plan is valid.
- [scripts/model.py](scripts/model.py): script defining the planGPT model.
### Installation
To install the required dependencies, run:
```bash 
cd scripts/
pip install -r requirements.txt
```
To note we provide more packages than needed, so it's possible to remove some of them if you have issues feel free to contact us by [email](mailto:massimiliano.tummolo@unibs.it).
In addition, you will need to download the models and datasets from the following links:
- Models: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10908361.svg)](https://doi.org/10.5281/zenodo.10908361)
- Datasets: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10925404.svg)](https://doi.org/10.5281/zenodo.10925404)


Furthermore, if you want, we provide all the generations of the plans in the following link: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10926333.svg)](https://doi.org/10.5281/zenodo.10926333) usable to be validated with the script validator.ipynb.
## Usage
### Plan Generation
First of all you need to generate the plans using the script plan_generator.py. The script requires the following arguments:
...

### Plan Validation
...
