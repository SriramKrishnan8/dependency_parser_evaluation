# Evaluating Samsaadhanii's Anusaarakam (Dependency Parser)

This package contains the script for evaluating the dependency parser results from Samsaadhanii's Anusaarakam using the gold data annotated with the Samsaadhanii dependency guidelines.

## Requirements:

1. [Samsaadhanii Platform](https://github.com/samsaadhanii/scl.git) is to be locally installed. 
2. Python requirements: pandas, numpy, tqdm.
3. *paths.py* should be updated based on the cgi-bin directory. 

## Usage:

```
sh run_all.sh
```

## Results:

1. All the gold .tsv files should be stored in the **gold_dir/**.
2. The dependency parser's results are obtained from the locally installed Samsaadhanii package and stored in **pred_dir/** in the .tsv format with the same name as in gold_dir/.
3. **result.tsv** stores the following results for each sentence:
    ```
    sentence_id, sentence, gold_relations, parser_status, predicted_relations, number of words without dependency predictions, label accuracy score (ls), unlabelled attachment score (uas), labelled attachment score (las)
    ```
4. **error.tsv** stores the sentence_id, sentence, gold_relations where the parser fails to produce any result.
5. **scores.json** stores the mean ls, uas and las scores.

For a sample analysis, gold_dir/ contains the gold dependency tags of Bhagavad Gītā's Chapter 12 verses. 