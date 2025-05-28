import os
import sys

import json

from tqdm import tqdm

from evaluate import run_sentences

script, gold_dir, pred_dir, out, err, res = sys.argv


def read_contents(name_):
    """ Returns the contents of the file as a list of lines """
    
    file_ = open(name_, "r", encoding="utf-8")
    file_contents = file_.read()
    file_.close()
    
    file_lines = list(filter(None, file_contents.split("\n")))
    
    return file_lines[1:]
    

gold_analyses = []

gold_sent_id = 0

list_of_files = sorted(os.listdir(gold_dir))

for f in tqdm(list_of_files, desc="Extracting Gold..."):
    f_name = os.path.join(gold_dir, f)
    f_lines = read_contents(f_name)
    
    gold_sent_id += 1
    sentence = ""
    details = []
    
    for x in f_lines[:]:
        entry = x.split("\t")
        
        index = entry[0]
        word = entry[1]
        relation = entry[6]
        
        if not index:               # Skip blank lines
            continue
        elif "(" in word:           # Skip words introduced in gold data for clarity
            continue
        elif "-" in word:           # Concatenate compound components
            sentence += word
        else:                       # Concatenate words with space
            sentence += word + " " 
        
        if not relation:
            relation = "-,-"
        elif relation == "-":
            relation = "-,-"
        
        modified_relation = relation
        # Choosing the first relation in case of multiple relations
        if "#" in relation:
            modified_relation = modified_relation.split("#")[0]
        
        # Choosing the first relation in case of multiple relations
        if ";" in relation:
            modified_relation = modified_relation.split(";")[0]
        
        # For obtaining the dependency tags according to the guidelines
        # of the parser. This is required when comparing the cpd type 
        # predictions
        if "," in modified_relation:
            rel_type, rel_index = modified_relation.split(",")
            # Temporarily commented this: Add maps to relations and then 
            # get corresponding relations 
#            rel = f"{get_code_for_relation(rel_type)},{rel_index}"
            modified_relation = f"{rel_type},{rel_index}"
        
        details.append((index, word, modified_relation))
    
    # For saving the prediction
    f_out = os.path.join(pred_dir, f)
    gold_analyses.append((gold_sent_id, f_out, sentence.strip(), details))

pred_analysis = []

overall_result, errors, temp_results = run_sentences(gold_analyses[:], "Unicode")

formatted_results = [ "\t".join(x) for x in temp_results ]
out_f = open(out, "w", encoding="utf-8")
out_f.write("\n".join(formatted_results))
out_f.close()

formatted_errors = [ "\t".join(x) for x in errors ]
err_f = open(err, "w", encoding="utf-8")
err_f.write("\n".join(formatted_errors))
err_f.close()

with open(res, "w", encoding="utf-8") as f:
    f.write(json.dumps(overall_result, ensure_ascii=False))
