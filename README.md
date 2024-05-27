# planGPT -     Learning General Policies for Planning through GPT Models
This repository includes  the provided code for the paper ```Learning General Policies for Planning through GPT Models```[(link)](https://openreview.net/pdf?id=yB8oafJ8bu).The scripts provided are:
- [scripts/plan_generator.py](scripts/plans_generator.py): script to generate plans given a dataset of planning problems.
- [scripts/validator.ipynb](scripts/validator.ipynb): script to validate the generated plans.
- [scripts/solver_pddl.py](scripts/solver_pddl.py): script to generate a planGPT plan using as input a PDDL problem.
- [scripts/metric.py](scripts/metric.py): script inspired by VAL that given an initial state, goal state, plan and domain verifies if the plan is valid.
- [scripts/model.py](scripts/model.py): script defining the planGPT model.
### Installation
The code is written in Python 3.8.10 and to install the required packages you can run the following command:
```bash 
cd scripts/
pip install -r requirements.txt
```
To note we provide more packages than needed, so it's possible to remove some of them if you have issues feel free to contact us by [email](mailto:massimiliano.tummolo@unibs.it).
In addition, for the dataset and models you will need to download them from the following links:
- *Models*: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10908361.svg)](https://doi.org/10.5281/zenodo.10908361)
- *Datasets*: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10925404.svg)](https://doi.org/10.5281/zenodo.10925404)


Furthermore, if you want, we provide all the *generations of the plans* in the following link: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10926333.svg)](https://doi.org/10.5281/zenodo.10926333) usable to be validated with the script [scripts/validator.ipynb](scripts/validator.ipynb).
## Usage
### Plan Generation
The generation of plans by planGPT can be done using the script [scripts/plan_generator.py](scripts/plans_generator.py). The script requires a configuration file in JSON format. An example of the configuration file is the following:
```json
{
    "dataset_dir": "DATASET_FOLDER",
    "tokenizer_dir": "MODEL_FOLDER",
    "model_dir": "MODEL_FOLDER",
    "output_dir": "WHERE_TO_SAVE_PLANS",
    "num_beams": 1,
    "num_return_sequences": 1,
    "percentage_actions_seen": 0,
    "batch_size": 1,
    "save_after": 100,
    "domain": "DOMAIN_NAME"
}
```
The parameters are:
- *dataset_dir*: the folder containing the dataset.
- *tokenizer_dir*: the folder containing the tokenizer.
- *model_dir*: the folder containing the model.
- *output_dir*: the folder where to save the generated plans.
- *num_beams*: the number of beams to use during the generation. For example, 1 means greedy search, 5 means beam search with 5 beams.
- *num_return_sequences*: the number of sequences to return. For example, 1 means return only the best sequence, 5 means return the 5 best sequences.
- *percentage_actions_seen*: the percentage of actions seen during the generation (0 means no actions seen, 100 means all actions of a correct plan seen).
- *batch_size*: the batch size to use during the generation.
- *save_after*: the number of generations after which save the results.
- *domain*: the domain name of the dataset. For example, blocksworld.

Then after creating the configuration file you can run the script with the following command:
```bash
cd scripts/
python plan_generator.py configuration.json
```
### Plan Validation
The validation of the generated plans can be done using the script [scripts/validator.ipynb](scripts/validator.ipynb). The only modification needed is to set the path of the generated plans in the variable ```folder_data_path```. So you can provide the path of the folder containing the generated plans using a custom script or the generation provided in the link above. 
