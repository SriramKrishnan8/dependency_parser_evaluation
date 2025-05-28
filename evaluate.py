import os
import sys

import json
import pandas as pd
import numpy as np

from tqdm import tqdm

from run_anusaaraka import test, get_dependency_annotation


def evaluation(gold_analysis, pred_analysis):
    """ 
    Compare the gold and predicted analysis and return the scores
    ls - label accuracy score
    uas - unlabelled attachment score
    las - labelled attachment score
    no_analysis - number of words for which dependency relation is not available
    """
    
    rel_type_matches = 0.0
    rel_index_matches = 0.0
    complete_rel_matches = 0.0

    no_analysis = 0

    for j in range(len(gold_analysis)):
        gold_index, gold_word, gold_relation = gold_analysis[j]
        pred_index, pred_word, pred_relation = pred_analysis[j]

        # To skip the punctuations
        if gold_word in ",.":
            continue
        
        # To have a standard representation of <rel_type>,<rel_index>
        # if not pred_relation or pred_relation == "-":
        #     pred_relation = "-,-"
        
        gold_rel_type, gold_rel_index = gold_relation.split(",")
        pred_rel_type, pred_rel_index = pred_relation.split(",")
        
        # Collecting the number of words for which dependency relation is not available
        if not pred_rel_type or pred_rel_type == "-":
            no_analysis += 1
        
        gold_rel_type = gold_rel_type.rstrip("-")
        # Temporarily commented. Add it based on the types
        # gold_rel_type = gold_map.get(gold_rel_type, gold_rel_type)
        
        # For uas
        if gold_rel_index == pred_rel_index:
            rel_index_matches += 1
        
        # For ls
        if gold_rel_type == pred_rel_type:
            rel_type_matches += 1
        # Uncomment the following based on the required types
#        elif gold_rel_type == get_code_for_relation(pred_rel_type):
#            rel_type_matches += 1
#        elif gold_rel_type == get_code_for_relation_2(pred_rel_type):
#            rel_type_matches += 1
            
        # Uncomment the following based on the required types
        # modified_pred_relation_1 = f"{get_code_for_relation(pred_rel_type)},{pred_rel_index}"
        # modified_pred_relation_2 = f"{get_code_for_relation_2(pred_rel_type)},{pred_rel_index}"
            
        # modified_gold_relation = f"{gold_rel_type},{gold_rel_index}"
        
        # For las
        if gold_relation == pred_relation:
            complete_rel_matches += 1
        # Uncomment the following based on the required types
#        elif modified_gold_relation == modified_pred_relation_1:
#            complete_rel_matches += 1
#        elif modified_gold_relation == modified_pred_relation_2:
#            complete_rel_matches += 1
            
    no_of_components_to_be_considered = len(gold_analysis) - 1
    
    ls = rel_type_matches / no_of_components_to_be_considered
    uas = rel_index_matches / no_of_components_to_be_considered
    las = complete_rel_matches / no_of_components_to_be_considered
    
    return ls, uas, las, no_analysis


def json_dump(x):
    """ """
    
    return json.dumps(x, ensure_ascii=False)


def handle_error(error):
    """ """

    error = error.replace("\n", " ")

    return error


def run_sentences(gold_analyses, encoding):
    """ """
    
    errors = []
    
    ls_scores = []
    uas_scores = [] 
    las_scores = []
    
    results = []
    
    for id_, file_, sent, gold_deprel in tqdm(gold_analyses, desc="Running Anusaaraka..."):
        
        res, status, error = test(sent, encoding)
        
        # If parser fails to produce any result
        if error or not status == "Success":
            error = handle_error(error)
            errors.append((str(id_), sent, json_dump(gold_deprel)))
            results.append((str(id_), sent, json_dump(gold_deprel), "Failure", error, "-", "-", "-", "-"))
            ls_scores.append(0.0)
            uas_scores.append(0.0)
            las_scores.append(0.0)
            continue
        
        pred_deprel, all_annotations = get_dependency_annotation(res)
        # If comppunds types are also considered, then dvandva analysis 
        # needs to be handled and the following should be uncommented.  
        # converted_deprel = handle_xvanxva(pred_deprel)
        
        # To generate the tsv file from the predictions
        for sent_id, annotations_pd in all_annotations:
            new_file_ = file_ + "_" + sent_id if len(all_annotations) > 1 else file_
            annotations_pd.to_csv(new_file_, sep='\t', index=False)
        
        ls, uas, las, no_analysis = evaluation(gold_deprel, pred_deprel)
        
        results.append((str(id_), sent, json_dump(gold_deprel), "Success", json_dump(pred_deprel), str(no_analysis), str(ls), str(uas), str(las)))
        
        ls_scores.append(ls)
        uas_scores.append(uas)
        las_scores.append(las)
    
    avg_ls_score = np.mean(ls_scores)*100.0
    avg_uas_score = np.mean(uas_scores)*100.0
    avg_las_score = np.mean(las_scores)*100.0
    
    scores = {
        "mean_ls" : avg_ls_score,
        "mean_uas" : avg_uas_score,
        "mean_las" : avg_las_score,
    }
    
    return scores, errors, results
    
