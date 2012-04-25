eval-c.py
---
- used a hash_table with `class_name` as key and another hash_table within as value.  
  eg. `results_hash['Arts']['precision']` returns the precision for __Arts__
- `calculate` method calls `calculate_class` method for each class in `classes.txt`
- classes not found in `classes.txt` are therefore ignored
- precision =  relevant_retrieved / retrieved
- recall = relevant_retrieved / relevant
- F1 = 2 * ( ( precision * recall ) / ( precision + recall ) )
- average calculated as according to lab description (macro averages)


eval-ir.py
---
- specified line is converted to a list  
  => `gold_list` and `predict_list`
- iterates through `predict_list` and check if item exists in `gold_list`
- used a list for each item in predict_list and a hash_table within as value  
  eg. `rank_hash[0]['precision']` returns the precision at Rank 1
- __precision__, __recall__ calculated as `eval-c.py`
- Interpolated precision calculated by going through the rank_hash from the last item  
	- iterate through and use the `max_precision` as current precicion
	- results in a non-increasing stair-like interpolated_precision/recall curve
 - __F1__ is then calculated with new interpolated precision


Files included with this submission
---
- eval-c.py <-- evaluation program for urls
- eval-ir.py <-- evaluation program for ranked retrieval
- urls.correct.txt <-- input for eval-c.py
- urls.predict.txt <-- gold standard input for eval-c.py
- output-file-of-results <-- input for eval-ir.py
- correct-file-of-results <-- gold standard input foreval-ir.py
