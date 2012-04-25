index.py
---
- a dictionary datatype is use to hold the all the terms.
- a dictionary is used so we can easily have unique entries only.
- the KEY will be the term-name and the VALUE will be the list-of-postings.
- the dictionary is than iterated at the end of the program to write it's key and post-listings into `dictionary.txt` and `postings.txt` respectively.

search.py
---
- query is parsed from infix to postfix(RPN) notation with AND a higher precedence than OR using the shuting-yard-algorithm (implemented using stacks)
- the string term in `dictionary.txt` is used to generate a QueryTerm object to hold it's name, ptr_pos, doc_freq, num_bytes and list-of-postings for each term used in queries.txt
- a cache `all_query_terms` is used to store QueryTerm objects that are created from previous queries to be reused
- a stack based evaluation is done in the end to process the postfix query.
- during intersecting of postings, as 2 whole line of post-listing for the 2 terms are loaded into the memory for comparison, there is no need to store the skip pointers in postings.txt and retrieve using pointers to skip terms.  
Instead, a `postings1[jump_factor_p1]` will be used to check if skipping is possible. Skipping is then implemented by splicing the posting-list by by a jump_factor amount to speed up intersection by doing less loops during due less comparisons.

dictionary.txt
---
FORMAT: 
	[key] [doc_freq] [ptr_pos] [num_bytes]

- 1 line represents a unique term and, it's post-listing is found in the corresponding line in postings.txt

- __ptr_pos__: pointer position to find the corresponding listing using `seek()` in postings.txt
- __num_bytes__: number of bytes to read in postings.txt to retrieve the postings for this key

- although __num_bytes__ can be calculated from the next line __ptr_pos__, it is still stored to save calculation time as storage is not a major concern for this assignment
- last line contains key `__ALLPOSTINGS__` for NOT operation

postings.txt
---
FORMAT:
	[doc_id], ... ,[doc_id]\n

- 1 line represents the post-listing for 1 key in the corresponding line in dictionary.txt in ASC order
- Last line contains list of all doc_ids for NOT operation

---

Files included with this submission
---

- index.py <-- indexing program
- search.py <-- search program
- dictionary.txt <-- dictionary (created by index.py)
- postings.txt <-- postings (created by index.py)
- queries.txt <-- queries to execute
- output.txt <-- results (created by search.py)