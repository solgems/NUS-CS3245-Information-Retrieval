index.py
--------
- removed __dictionary-as-a-string__
- stores term frequency instead of individual term positions


dictionary.txt
--------------
FORMAT:
	[term] [doc-freq] [posting-pointer(linenumber)]


postings.txt
------------
FORMAT:
	[(doc-id), term-frequency)]

1 line represents the post-listing for 1 unique term found in the corresponding line in `dictionary.txt`


search.py
---------
- removed tree structure and back to the old hash-table
- each `QueryTerm` consist of `.name` `.doc_freq` `.postings` and `.idf`
- uses a simple cache `all_query_terms_cache` to reuse `QueryTerm` so as to reduce postings read from disk
- query is parsed and chopped into a list with repeated stemmed words removed
- a original query is stored to count the of repeated stemmed terms for query's TF
- query terms that don't exist in the dictionary are ignored as they contribute 0 to score
- used algorithm on slide 39 of lecture 7 for the computing of scores
	- performs ** (query-vector DOT doc-vector) / (length of query-vector) **
- follows the __lnn.ltc__ convention
- the results are stored in a hash-table named scores
- FORMAT:  
	`scores = {docid: score-value}`
- results is therefore sorted by descending `value(score)` then ascending `key(doc-id)` for same scores
- returns at most K top results, constant modifiable at top of file

---

Files included with this submission
---
- index.py <-- indexing program
- search.py <-- search program
- dictionary.txt <-- dictionary (created by index.py)
- postings.txt <-- postings (created by index.py)
- queries.txt <-- queries to execute
- output.txt <-- results (created by search.py)