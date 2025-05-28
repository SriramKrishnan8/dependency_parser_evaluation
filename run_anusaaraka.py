import os
import sys

import subprocess as sp

import json
import pandas as pd

from paths import *


def call_anusaaraka(encoding, splitter, out_encoding, parse,
                    text_type, tlang, mode, text):
    """
    Call the anusaaraka.cgi script with the given parameters
    """
    
    env_vars = [
        "encoding=" + encoding,
        "splitter=" + splitter,
        "out_encoding=" + out_encoding,
        "parse=" + parse,
        "text_type=" + text_type,#.replace(" ", "+"),
        "tlang=" + tlang,
        "mode=" + mode,
        "text=" + text,
    ]
    
    query_string = "QUERY_STRING=\"" + "&".join(env_vars) + "\""
    command = query_string + " " + cgi_file
    
    original_cwd = os.getcwd()
    
    # Change working directory to call SCL's anusaaraka.cgi
    os.chdir(cgi_path)
    
    try:
        p = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        outs, errs = p.communicate()
    except Exception as e:
        result = ""
        status = "Failed: " + str(e)
    else:
        result = outs.decode('utf-8')
        status = "Success"
        error = errs.decode('utf-8')
    finally:
        # Restore the original working directory
        os.chdir(original_cwd)
    
    return result, status, error


def test(sentence, encoding):
    """

    """
    
    splitter = "None"
    out_encoding = "Devanagari"
    parse = "full"
    text_type = "Sloka"
    tlang = "Hindi"
    mode = "json"
    
    res, status, error = call_anusaaraka(
        encoding, splitter, out_encoding, 
        parse, text_type, tlang, mode, sentence
    )
    
    return res, status, error


def get_dependency_annotation(dep_res_json_str):
    """
    Extract index, word and dependency relations
    from the JSON string 
    """
    
    dep_res_json_str = dep_res_json_str.split("\n")[-1]
    dep_res_json = json.loads(dep_res_json_str)
    annotated_sentences = []
    all_annotations = []
    sent_id = 1
    for sent_json in dep_res_json:
        sent_analysis = sent_json["sent"]
        
        dep_rel = []
        for word_json in sent_analysis:
            index = word_json["index"]
            word = word_json["word"]
            rel = word_json["kaaraka_sambandha"]

            if not rel:
                rel = "-,-"
            elif rel == "-":
                rel = "-,-"
            
            # Choosing the first relation
            if ";" in rel:
                rel = rel.split(";")[0]
            if "#" in rel:
                rel = rel.split("#")[0]
            
            # Extracting the maps of relations
            # To be used when compound types are considered
            if "," in rel:
                rel_type, rel_index = rel.split(",")
                # Temporarily commented this: Add maps to relations and then 
                # get corresponding relations 
#                rel = f"{get_code_for_relation(rel_type)},{rel_index}"
                rel = f"{rel_type},{rel_index}"
            dep_rel.append((index, word, rel))
        
        annotated_sentences.append(dep_rel)
        
        sent_analysis_str = json.dumps(sent_analysis, ensure_ascii=False)
        sent_pd = pd.read_json(sent_analysis_str, orient='records')
        all_annotations.append((f"{sent_id}", sent_pd))
        sent_id += 1
        
    return annotated_sentences[0] if len(annotated_sentences) > 0 else [], all_annotations


def run_samsaadhanii_parser(sentence, encoding):
    """ """
    
    res, status, error = test(sentence, encoding)
    pred_annotations = get_dependency_annotation(res)
    
    return pred_annotations


#pred_annotations = run_samsaadhanii_parser("धर्म-क्षेत्रे कुरु-क्षेत्रे समवेताः युयुत्सवः मामकाः पाण्डवाः च एव किम् अकुर्वत सञ्जय", "Unicode")
#status_str = [ "\t".join(x) for x in pred_annotations ]
#print("\n".join(status_str))



















