# Script for generating plans from the test dataset.
# The generated plans are saved in the specified output directory
# using the provided options. If no actions are added to the input,
# the generated plans will be saved in the "0_actions" directory.
# If one action is added to the input, the plans will be saved in the
# "1_actions" directory, and so on.
# Currently, there is no loop over the number of actions. To generate
# plans with zero actions in the input, the script needs to be run once.
# To generate plans with a percentage of actions in the input, the script needs to be
# run again, and so on.
import time

import torch
import sys
import os
import json
import logging
import random
from tqdm import tqdm
from dataclasses import dataclass, field

from datasets import load_from_disk, load_dataset
from torch.utils.data import DataLoader
from pathlib import Path
from model import GPT2PModel

from transformers import (
    HfArgumentParser,
    DataCollatorForLanguageModeling,
    AutoTokenizer,
)
from datasets import Dataset
import pandas as pd

from typing import Optional
import metric


# Class used to define the possible arguments for training
@dataclass
class PlanGenerationArgs:
    """
    Options for plan generation.
    """

    dataset_dir: Optional[str] = field(
        default="dataset/json/logistics_invariants/20_plans.json",
        metadata={"help": "Folder containing the dataset."},
    )
    tokenizer_dir: Optional[str] = field(
        default="",
        metadata={"help": "Folder containing the tokenizer."},
    )
    model_dir: Optional[str] = field(
        default="",
        metadata={"help": "Folder containing the model."},
    )
    output_dir: Optional[str] = field(
        default="output", metadata={"help": "Folder where to save the generated plans."}
    )
    max_length: Optional[int] = field(
        default=2048,
        metadata={"help": "Maximum length of the generated plan. Default is 2048."},
    )
    num_beams: Optional[int] = field(
        default=1,
        metadata={
            "help": "Number of beams to use during generation. Default is 1 (greedy)."
        },
    )
    percentage_actions_seen: Optional[int] = field(
        default=0,
        metadata={"help": "Percentage of actions to show in the generated plan."},
    )
    pddl_dir: Optional[str] = field(
        default="pddl",
        metadata={"help": "Pddl directory containing the domain and problem files."},
    )
    pddl_domain_file: Optional[str] = field(
        default="domain.pddl",
        metadata={"help": "File containing the domain definition."},
    )
    log_file_name: Optional[str] = field(
        default="generation.log", metadata={"help": "File where to save the logs."}
    )
    batch_size: Optional[int] = field(
        default=4, metadata={"help": "Batch size for generation. Default is 4."}
    )
    save_after: Optional[int] = field(
        default=10,
        metadata={"help": ("Save the output to file every save_after steps. ")},
    )
    sort_initial_state: Optional[bool] = field(
        default=True, metadata={"help": "Sort the initial state fluents."}
    )
    seed: Optional[int] = field(default=7, metadata={"help": "Seed."})
    top_k: Optional[int] = field(
        default=-1, metadata={"help": "If > 0, use top-k sampling. Default is -1."}
    )
    top_p: Optional[float] = field(
        default=-1, metadata={"help": "If > 0, use top-p sampling. Default is -1."}
    )
    num_return_sequences: Optional[int] = field(
        default=1, metadata={"help": "Number of sequences to generate. Default is 1."}
    )
    domain: Optional[str] = field(
        default="logistics",
        metadata={"help": "Domain of the dataset. Default is logistics."},
    )
    is_old_model: Optional[bool] = field(
        default=False, metadata={"help": "DEPRECATED: To indicate if the model is old."}
    )
    super_model: Optional[bool] = field(
        default=False,
        metadata={
            "help": "DEPRECATED: To indicate if the model is super (it was an old version of PlanGPT, which separated even the numbers from the object names)."
        },
    )
    reverse: Optional[bool] = field(
        default=False,
        metadata={
            "help": "DEPRECATED: To indicate if the model is reverse (another older version of PlanGPT, trained to generated a plan from the last action till the first)."
        },
    )


logger = logging.getLogger(__name__)


def main():
    # Parsing of the arguments
    parser = HfArgumentParser(PlanGenerationArgs)
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        (args,) = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        (args,) = parser.parse_args_into_dataclasses()
    # Creating the output directory
    tmp_plan_dir = f"{args.percentage_actions_seen}_actions"
    if args.top_k > 0:
        tmp_plan_dir = tmp_plan_dir + f"_top_k_{args.top_k}"
    if args.top_p > 0:
        tmp_plan_dir = tmp_plan_dir + f"_top_p_{args.top_p}"
    plan_output_dir = Path(args.output_dir, tmp_plan_dir)
    plan_output_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = plan_output_dir.joinpath(args.log_file_name)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file_path),
        ],
    )

    # Loading the dataset, tokenizer, and model

    if args.is_old_model:
        dataset = load_dataset("json", data_dir=args.dataset_dir)
    else:
        dataset = load_from_disk(args.dataset_dir)
    logger.info(dataset)
    logger.info(dataset["train"][0])
    logger.info("Dataset loaded successfully")
    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer_dir,
        unk_token="<|unknown|>",
        pad_token="<|pad|>",
        bos_token="<|startofplan|>",
        eos_token="<|endofplan|>",
        mask_token="<|mask|>",
        additional_special_tokens=["<|goals|>", "<|actions|>"],
        padding_side="right",
    )
    model = GPT2PModel.from_pretrained(args.model_dir, device_map="auto")
    logger.info(model)
    logger.info(tokenizer)
    random.seed(args.seed)

    # Preprocessing the dataset
    dataset = dataset["test"]
    logger.info("Removing duplicates..")

    df = pd.DataFrame(dataset)
    uniques = df["pddl_problem_file"].nunique()
    logger.info(f"Number of unique problems :{uniques}")
    df = df.drop_duplicates(subset="pddl_problem_file")
    new_dataset = Dataset.from_pandas(df)
    if "__index_level_0__" in new_dataset.column_names:
        new_dataset = new_dataset.remove_columns(["__index_level_0__"])

    logger.info(f"Original dataset dim: {len(dataset)}")
    logger.info(f"New dataset dim: {len(new_dataset)}")

    dataset = new_dataset
    to_remove_column_names = [
        "name",
        "initial_state",
        "goals",
        "len_initial_state",
        "len_goals",
        "len_plan",
        "pddl_problem_file",
    ]

    # Preprocessing function
    def shuffle_or_not_shuffle(examples):
        output = []
        for state, goals, actions in zip(
            examples["initial_state"], examples["goals"], examples["actions"]
        ):

            if args.sort_initial_state:
                state = metric.unite_actions(
                    state,
                    list(metric.dict_predicates_domain[args.domain].keys()),
                    args.domain,
                )
                state = [x.replace("_", " ") for x in state]
                state = sorted(state)
                state = " ".join(state)
                goals_list = metric.unite_actions(
                    goals,
                    list(metric.dict_predicates_domain[args.domain].keys()),
                    args.domain,
                )
                goals_list = [x.replace("_", " ") for x in goals_list]
                goals_list = sorted(goals_list)
                goals = " ".join(goals_list)

            new_state = state + " <|goals|> " + goals

            new_state = new_state + " <|actions|> "
            action_list = actions.split(" ")
            if args.percentage_actions_seen > 0:
                actions_plan = metric.unite_actions(
                    " ".join(action_list),
                    list(metric.dict_actions_domain[args.domain].keys()),
                    args.domain,
                )
                num_actions_to_show = int(
                    len(actions_plan) * args.percentage_actions_seen / 100.0
                )
                actions_plan = actions_plan[:num_actions_to_show]
                action_string = " ".join(actions_plan).replace("_", " ")
            else:
                action_string = ""
            if action_string != "":
                new_state = new_state + " " + action_string
            output.append(new_state)
        return {"states": output}

    # Tokenization function
    def tokenize_function(examples):
        return tokenizer(
            examples["states"],
            return_token_type_ids=False,
        )

    # First preprocessing of the dataset
    pre_processed_datasets = dataset.map(
        shuffle_or_not_shuffle,
        batched=True,
        remove_columns=to_remove_column_names,
        desc=(
            "Sort initial state fluents for every example of the dataset"
            if (args.sort_initial_state)
            else "Concatenation of initial state and goals"
        ),
    )

    tokenized_datasets = pre_processed_datasets.map(
        tokenize_function,
        batched=True,
        remove_columns=["actions", "states"],
        desc="Running tokenizer on dataset",
    )

    test_dataset = tokenized_datasets

    logger.info(test_dataset)
    logger.info("You can safely ignore the warning above ^^")

    for index in random.sample(range(len(test_dataset)), 3):
        logger.info(f"Sample {index} of the training set: {test_dataset[index]}")
        logger.info(
            f"Sample {index} of the training set, shape: {len(test_dataset[index]['input_ids'])}"
        )
        logger.info(
            f'Decoded sample {index} of the training set: {tokenizer.decode(test_dataset[index]["input_ids"])}'
        )
        action_idx = test_dataset[index]["actions_idx"]
        logger.info(
            f"Check if {index} of the training set has the correct value (<|action|>): {tokenizer.decode(test_dataset[index]['input_ids'][action_idx])}."
        )

    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    test_dataloader = DataLoader(
        test_dataset,
        collate_fn=data_collator,
        batch_size=args.batch_size,
        drop_last=False,
    )

    logger.info("Starting generation of plans")
    logger.info(f"Dataset size: {len(tokenized_datasets)}")

    bounds = (0, 0)

    actions_token_id = tokenizer.convert_tokens_to_ids("<|actions|>")
    generation_output = []
    for step, batch in enumerate(tqdm(test_dataloader)):
        problem_ids_list = []
        example_ids_list = []
        for i in range(batch["input_ids"].shape[0]):
            instance = dataset[step * args.batch_size + i]["name"].split("-")[-1]
            problem_id = dataset[step * args.batch_size + i]["pddl_problem_file"].split(
                "."
            )[0]
            example_id = instance.split(".")[0]
            problem_ids_list.append(problem_id)
            example_ids_list.append(example_id)
        inputs = batch["input_ids"]
        inputs = inputs.to("cuda:0")
        start_time = time.time()
        with torch.no_grad():
            if args.top_k > 0 and args.top_p == -1:
                outputs = model.generate(
                    inputs,
                    num_return_sequences=args.num_return_sequences,
                    do_sample=True,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                    top_k=args.top_k,
                )

            elif args.top_p > 0 and args.top_k == -1:
                outputs = model.generate(
                    inputs,
                    num_return_sequences=args.num_return_sequences,
                    do_sample=True,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                    top_p=args.top_p,
                )
            elif args.top_p > 0 and args.top_k > 0:
                outputs = model.generate(
                    inputs,
                    do_sample=True,
                    max_length=args.max_length,
                    num_return_sequences=args.num_return_sequences,
                    pad_token_id=tokenizer.pad_token_id,
                    top_k=args.top_k,
                    top_p=args.top_p,
                )
            else:
                outputs = model.generate(
                    inputs,
                    num_beams=args.num_beams,
                    num_return_sequences=args.num_return_sequences,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                )
        end_time = time.time()
        for i in range(batch["input_ids"].shape[0]):
            results = []
            for j in range(args.num_return_sequences):
                if (
                    batch["input_ids"].shape[0] == 1
                ):  # If batch size is 1, outputs is a tensor
                    generated_plan = outputs[j]
                else:
                    generated_plan = outputs[i][j]

                if tokenizer.eos_token_id in generated_plan:
                    found_eos = True
                else:
                    found_eos = False

                if generated_plan[-1] == tokenizer.eos_token_id:
                    generated_plan = generated_plan[:-1]
                else:
                    eop_idx = (generated_plan == tokenizer.eos_token_id).nonzero(
                        as_tuple=True
                    )[0]
                    if eop_idx.shape[0]:
                        generated_plan = generated_plan[: eop_idx[-1]]
                    else:
                        pad_idx = (generated_plan == tokenizer.pad_token_id).nonzero(
                            as_tuple=True
                        )[0]
                        if pad_idx.shape[0]:
                            generated_plan = generated_plan[: pad_idx[0]]

                actions_idx = batch["actions_idx"][i]
                generated_plan = generated_plan[actions_idx + 1 :]

                sop_idx = (batch["input_ids"][i] == tokenizer.bos_token_id).nonzero(
                    as_tuple=True
                )[0]
                input_to_decode = batch["input_ids"][i, sop_idx:]
                super_model = args.super_model
                import re

                def remove_blanks(stringa):
                    return re.sub(r"\s+(\d)", r"\1", stringa)

                if super_model:
                    plan = remove_blanks(tokenizer.decode(generated_plan))
                else:
                    plan = tokenizer.decode(generated_plan)

                if args.reverse:
                    actions_plan = metric.unite_actions(
                        plan,
                        list(metric.dict_actions_domain[args.domain].keys()),
                        args.domain,
                    )
                    actions_plan.reverse()
                    plan = " ".join(actions_plan)
                results.append(plan)
            generation_output.append(
                {
                    "input": tokenizer.decode(input_to_decode),
                    "plan": results if args.num_return_sequences > 1 else results[0],
                    "percentage_actions_seen": args.percentage_actions_seen,
                    "problem_id": problem_ids_list[i],
                    "example_id": example_ids_list[i],
                    "time": end_time - start_time,
                    "found_eos": found_eos,
                }
            )

        q, r = divmod(step, args.save_after)
        if r == (args.save_after - 1):
            if (q + 1) * args.batch_size - 1 <= len(test_dataset) - 1:
                bounds = (
                    q * args.save_after * args.batch_size,
                    (step + 1) * args.batch_size - 1,
                )
                logger.info(
                    f"Generated {(step+1) * args.batch_size} plans of {len(test_dataset)}"
                )
                write_output_to_file(
                    output_dir=plan_output_dir,
                    generation_output=generation_output,
                    bounds=bounds,
                )
                generation_output = []

    logger.info("All plans have been generated")
    if bounds[1] + 1 <= len(test_dataset) - 1:
        bounds = (bounds[1] + 1, len(test_dataset) - 1)
        write_output_to_file(
            output_dir=plan_output_dir,
            generation_output=generation_output,
            bounds=bounds,
        )


def write_output_to_file(output_dir=None, generation_output=None, bounds=None):
    txt_path = Path(output_dir, f"output_{bounds[0]}_{bounds[1]}.txt")
    json_path = Path(output_dir, f"to_validate_{bounds[0]}_{bounds[1]}.json")
    logger.info(f"Writing outputs to files {txt_path} and {json_path}")
    with open(txt_path, "w") as output_file:
        for idx, example_output in enumerate(generation_output):
            output_file.write(f"***** Evaluation on example {idx}  *****\n")
            output_file.write(f"--- input: {example_output['input']}\n")
            output_file.write(
                f"--- percentage_actions_seen: {example_output['percentage_actions_seen']}\n"
            )
            output_file.write(f"--- generated_plan: {example_output['plan']}\n")
            output_file.write(f"--- example: {example_output['example_id']}\n")

    with open(json_path, "w") as output_file:
        json.dump(generation_output, output_file, indent=4)
    logger.info("Output files written successfully")


if __name__ == "__main__":
    main()
