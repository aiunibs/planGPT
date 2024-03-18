# Script per generare dei piani a partire dal dataset di test.
# I piani generati vengono salvati nella cartella di output indicata
# tramite le opzioni. Nel caso non si aggiunga alcuna azione all'input
# i piani generati verranno salvati nella cartella 0_actions, con un'azione
# in input nella cartella 1_actions e così via.
# Al momento non viene fatto un loop sul numero di azioni: per generare i
# piani con zero azioni in input bisogna lanciare lo script una volta, per
# generare i piani con una azione input bisogna lanciare lo script un'altra
# volta e così via.
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
import new_rewards as metric


# Definizione delle possibili opzioni
@dataclass
class PlanGenerationArgs:
    """
    Opzioni per la generazione dei piani.
    """
    dataset_dir: Optional[str] = field(
        default="dataset/json/logistics_invariants/20_plans.json",
        metadata={"help": "File relativo al test set da utilizzare."},
    )
    tokenizer_dir: Optional[str] = field(
        default="",
        metadata={"help": "Cartella contenente i file del tokenizer."},
    )
    model_dir: Optional[str] = field(
        default="",
        metadata={"help": "Cartella contenente i file del modello."},
    )
    output_dir: Optional[str] = field(
        default="output", metadata={"help": "Cartella di output."}
    )
    max_length: Optional[int] = field(
        default=2048,
        metadata={"help": "Lunghezza massima dei piani"},
    )
    num_beams: Optional[int] = field(
        default=1,
        metadata={"help": "Numero di beam per la generazione utilizzando la beam search. Valore di default è 1, che significa generazione greedy."}
    )
    percentage_actions_seen: Optional[int] = field(
        default=0, metadata={"help": "Numero di azioni da aggiungere all'input iniziale."}
    )
    pddl_dir: Optional[str] = field(
        default="pddl",
        metadata={"help": "Cartella dei file PDDL dei problemi"},
    )
    pddl_domain_file: Optional[str] = field(
        default="domain.pddl",
        metadata={"help": "Nome del file che contiene la definizione del dominio"},
    )
    log_file_name: Optional[str] = field(
        default="generation.log", metadata={"help": "Nome del file di log."}
    )
    batch_size: Optional[int] = field(
        default=4, metadata={"help": "Batch size da usare durante la generazione."}
    )
    save_after: Optional[int] = field(
        default=10,
        metadata={
            "help": (
                "Dopo quante batch vuoi salvare l'output della generazione "
                "per esempiop se batch_size è 4 e save_after è 10, allora "
                "dopo 10 batch l'output sarà salvato, ovvero il file conterrà 40 piani generati."
            )
        },
    )
    sort_initial_state: Optional[bool] = field(
        default=True, metadata={"help": "Per indicare se è necessario fare lo shuffle dello stato iniziale."}
    )
    seed: Optional[int] = field(
        default=7, metadata={"help": "Seed per riproducibilità dei risultati."}
    )
    is_old_model: Optional[bool] = field(  
        default=False, metadata={"help": "Per indicare se il modello è vecchio."}
    )
    super_model: Optional[bool] = field(
        default=False, metadata={"help": "Per indicare se il modello è super."})
    reverse: Optional[bool] = field(
        default=False, metadata={"help": "Per indicare se il modello è reverse."})
    top_k: Optional[int] = field(
        default=-1, metadata={"help": "Per indicare se è da usare top-k"})
    top_p: Optional[float] = field(
        default=-1, metadata={"help": "Per indicare se è da usare top-p"})
    num_return_sequences: Optional[int] = field(
        default=1, metadata={"help": "Per indicare se è da usare la beam search"})
    domain: Optional[str] = field(
        default="logistics", metadata={"help": "Nome del dominio"})

logger = logging.getLogger(__name__)


def main():
    # Parsing delle opzioni
    parser = HfArgumentParser(PlanGenerationArgs)
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        (args,) = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        (args,) = parser.parse_args_into_dataclasses()
    print(args.top_k)
    print(args.num_return_sequences)
    # Creazione delle cartelle di output e setup del logging
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

    # Caricamento del dataset, del tokenizer e del modello

    if args.is_old_model:
        dataset = load_dataset("json", data_dir=args.dataset_dir)
    else:    
        dataset = load_from_disk(args.dataset_dir)
    logger.info(dataset)
    logger.info(dataset['train'][0])
    logger.info("Dataset loaded successfully")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_dir,
        unk_token="<|unknown|>",
        pad_token="<|pad|>",
        bos_token="<|startofplan|>",
        eos_token="<|endofplan|>",
        mask_token="<|mask|>",
        additional_special_tokens=["<|goals|>", "<|actions|>"],
        padding_side='right')
    model = GPT2PModel.from_pretrained(args.model_dir, device_map="auto")
    logger.info(model)
    logger.info(tokenizer)
    random.seed(args.seed)

       # Preprocessing del dataset e tokenizzazione
    dataset = dataset["test"]       
    logger.info('Rimozione esempi duplicati...')

    df = pd.DataFrame(dataset) 
    valori_univoci = df["pddl_problem_file"].nunique()
    logger.info(f"Numero di valori univoci nella colonna dei problemi:{valori_univoci}")
    # Rimuovi i duplicati basandoti su una o più colonne specifiche
    df = df.drop_duplicates(subset="pddl_problem_file")

    # Ora converti il DataFrame nuovamente in un dataset
    new_dataset = Dataset.from_pandas(df)
    new_dataset = new_dataset.remove_columns(['__index_level_0__'])
    logger.info(f'Dimensione originale del dataset: {len(dataset)}')
    logger.info(f'Nuova dimensione del dataset: {len(new_dataset)}')

    dataset = new_dataset
    # Colonne superflue da rimuovere poi
    to_remove_column_names = ["name", "initial_state", "goals", "len_initial_state", "len_goals", "len_plan", "pddl_problem_file"]

    # Funzione di preprocessing che impila goals e stato iniziale
    def shuffle_or_not_shuffle(examples):
        output = []
        for state, goals, actions in zip(examples["initial_state"], examples["goals"], examples["actions"]):
            
            if args.sort_initial_state:
                # Shuffle stato iniziale
                state = metric.unite_actions(state, 
                                             list(metric.dict_predicates_domain[args.domain].keys()),
                                             args.domain,)
                #random.shuffle(state)
                #if args.domain == "satellite":
                #    types_predicates_name = ['satellite', 'direction', 'instrument', 'mode',]
                #    types_preds = [x for x in state if x.split('_')[0] in types_predicates_name]
                #    #print(types_preds)
                #    state = set(state) - set(types_preds)
                #    #print(state)
                #   state = sorted(types_preds) + sorted(state)
                #  #print(state)
                #    state = " ".join(state).replace('_', ' ')
                #else:
                state = [x.replace("_", " ") for x in state]
                state = sorted(state)
                #state = " ".join(state).replace('_', ' ')
                state = " ".join(state)
                # Shuffle goals
                goals_list = metric.unite_actions(goals,
                                                    list(metric.dict_predicates_domain[args.domain].keys()),
                                                    args.domain,)
                #random.shuffle(goals_list)
                goals_list = [x.replace("_", " ") for x in goals_list]
                goals_list = sorted(goals_list)
                goals = " ".join(goals_list)

            
            new_state = state + " <|goals|> " + goals
            
            new_state = new_state + " <|actions|> "
            action_list = actions.split(" ")
            if args.percentage_actions_seen > 0:
                # VA SOLO PER LOGISTICS -> sistemalo
                # Unisco le azioni ne prendo la percentuale e poi le ridivido
                actions_plan = metric.unite_actions(" ".join(action_list), 
                                                    list(metric.dict_actions_domain[args.domain].keys()), 
                                                    args.domain)
                num_actions_to_show = int(len(actions_plan) * args.percentage_actions_seen/100.0) 
                actions_plan = actions_plan[:num_actions_to_show]
                action_string = " ".join(actions_plan).replace('_', ' ')
            else:
                # Non faccio nulla
                action_string = ""
            if action_string != "":
                new_state = new_state + " " + action_string
            output.append(new_state)
        return {"states": output}
    
    # Funzione di tokenizzazione che preso un piano tokenizza lo stato iniziale + goals 
    def tokenize_function(examples):
        return tokenizer(
            examples["states"],
            # Non aggiunta la traccia
            return_token_type_ids=False,
        )
    #Primo pre-processing del dataset
    pre_processed_datasets = dataset.map(
            shuffle_or_not_shuffle,
            batched=True,
            remove_columns=to_remove_column_names,
            desc=
                "Sort initial state fluents for every example of the dataset" if (args.sort_initial_state) 
                else "Concatenation of initial state and goals",)

    tokenized_datasets = pre_processed_datasets.map(
            tokenize_function,
            batched=True,
            remove_columns=['actions', 'states'],
            desc="Running tokenizer on dataset",
    )
    
    test_dataset = tokenized_datasets

    #test_dataset = test_dataset.select(range(100))
    logger.info(test_dataset)
    logger.info("You can safely ignore the warning above ^^")

    for index in random.sample(range(len(test_dataset)), 3):
        logger.info(f"Sample {index} of the training set: {test_dataset[index]}")
        logger.info(f"Sample {index} of the training set, shape: {len(test_dataset[index]['input_ids'])}")
        logger.info(f'Decoded sample {index} of the training set: {tokenizer.decode(test_dataset[index]["input_ids"])}')
        action_idx = test_dataset[index]['actions_idx']
        logger.info(f"Check if {index} of the training set has the correct value (<|action|>): {tokenizer.decode(test_dataset[index]['input_ids'][action_idx])}.")


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
            instance = dataset[step * args.batch_size + i]["name"].split("-")[
                -1
            ]
            problem_id = dataset[step * args.batch_size + i]["pddl_problem_file"].split(".")[0]
            example_id = instance.split(".")[0]
            problem_ids_list.append(problem_id)
            example_ids_list.append(example_id)
        inputs = batch["input_ids"]
        inputs = inputs.to("cuda:0")
        start_time = time.time()
        with torch.no_grad():
            if args.top_k > 0 and args.top_p == -1:
                # Usare solo top-k
                outputs = model.generate(
                    inputs,
                    num_return_sequences=args.num_return_sequences,
                    do_sample=True,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                    top_k=args.top_k,)
                
            elif args.top_p > 0 and args.top_k == -1:
                # Usare solo top-p
                outputs = model.generate(
                    inputs,
                    num_return_sequences=args.num_return_sequences,
                    do_sample=True,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                    top_p=args.top_p,)
            elif args.top_p > 0 and args.top_k > 0:
                # Usare sia top-k che top-p
                outputs = model.generate(
                    inputs,
                    do_sample=True, 
                    max_length=args.max_length,
                    num_return_sequences=args.num_return_sequences,
                    pad_token_id=tokenizer.pad_token_id,
                    top_k=args.top_k,
                    top_p=args.top_p,)
            else:   
                # Usare solo greedy      
                outputs = model.generate(
                    inputs,
                    num_beams=args.num_beams,
                    num_return_sequences=args.num_return_sequences,
                    max_length=args.max_length,
                    pad_token_id=tokenizer.pad_token_id,
                )
        end_time = time.time()
        for i in range(batch["input_ids"].shape[0]):# Itero sul batch_size
            results = []
            for j in range(args.num_return_sequences): # Itero sul numero di sequenze generate
                if batch["input_ids"].shape[0] == 1: # Se il batch_size è 1. ATTENZIONE LA GENERAZIONE VA SOLO CON BATCH_SIZE = 1
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
                    eop_idx = (generated_plan == tokenizer.eos_token_id).nonzero(as_tuple=True)[0]
                    if eop_idx.shape[0]:
                        generated_plan = generated_plan[:eop_idx[-1]]
                    else:
                        pad_idx = (generated_plan == tokenizer.pad_token_id).nonzero(as_tuple=True)[0]
                        if pad_idx.shape[0]:
                            generated_plan = generated_plan[:pad_idx[0]]
            
                #actions_idx = (generated_plan == actions_token_id).nonzero(as_tuple=True)[0]
                #actions_idx = torch.where(generated_plan == actions_token_id)[0]
                actions_idx = batch["actions_idx"][i]
                #print(tokenizer.decode(generated_plan))
                #print(f"Real action id: {real_action_id}")
                #print(f"Generated action id: {actions_idx}")
                generated_plan = generated_plan[actions_idx + 1:]

                sop_idx = (batch["input_ids"][i] == tokenizer.bos_token_id).nonzero(
                    as_tuple=True
                )[0]
                input_to_decode = batch["input_ids"][i, sop_idx:]
                super_model = args.super_model
                import re

                def rimuovi_spazi(stringa):
                    return re.sub(r'\s+(\d)', r'\1', stringa)
                if (super_model):
                    plan = rimuovi_spazi(tokenizer.decode(generated_plan))
                else:
                    plan = tokenizer.decode(generated_plan)
                
                # TODO: Attenzione per le azioni in percentuale in ingresso bisogna fare il reverse anche della traccia
                # TODO: reverse va solo con logistics da modificare lo script di preproccesser.
                if args.reverse:
                    actions_plan = metric.unite_actions(plan, 
                                                        list(metric.dict_actions_domain[args.domain].keys()), 
                                                        args.domain)
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
            output_file.write(f"--- percentage_actions_seen: {example_output['percentage_actions_seen']}\n")
            output_file.write(f"--- generated_plan: {example_output['plan']}\n")
            output_file.write(f"--- example: {example_output['example_id']}\n")

    with open(json_path, "w") as output_file:
        json.dump(generation_output, output_file, indent=4)
    logger.info("Output files written successfully")


if __name__ == "__main__":
    main()
