index.py
--------
- same as lab2 but switched to using linecache for smaller posting_ptrs
- implemented and switched to dictionary-as-a-string format

search.py
--------
Highlights:

- infinite length of phrasal queries
- prefix search __app__ returns all `doc_ids` that contains __application__ and __apple__ too.  
eg. if __application__ = [6], __apple__ = [2,4], therefore, __appl__ returns [2,4,6], whereas __appli__ returns [6]
- prefix and phrasal queries works together! This is all thanks to the tree search structure and positional indexing eg. searching __"n u s"__ will return all docs that contains __"national university singapore"__ and __"new unique sunflower"__

Additional information:

- query is parsed with double quotes as `+`  
eg. (`"apple pear orange"`) ==> (`apple + pear + orange`) ==> convert to postfix (`orange pear apple + +`)
- query is parsed from infix to postfix(RPN) notation with `+` gaining a slightly higher precedence than `AND`
- phrasal query, the `+` operation is implemented similarly to the `AND` operation just that this times it merges `word_positions` instead of `doc_ids`.

BUILDING THE TREE:

- after `dictionary.txt` into a buffer list, a root `TreeNode` object is created and stored in the `DictionaryMemoryTree` object.
- `DictionaryMemoryTree` is the handler layer that performs adding and searching of nodes on the Tree.
- after finding the name by using the `term_ptr`, the name is chopped up into a list, eg. 'ape' = `['a','p','e']`.  
a node `[a]` is created and appended as a child of the root if no other  exists.  
recursively, `[p]` is appended as a child of `[a]` and `[e]` as a child of `[p]`.  
The `[freq, postings_ptr]` of __ape__ is stored at the last node, node `[p]`.
- after adding another term __apple__, the tree looks like this:  
	`[root]-[a]-[#p]-[p]-[l]-[*e]`  
	`[#p]-[**e]`	
	- note that `[#p]` is the same node (just trying to illustrate it by typing it out)
	- `[*e]` contains the `[freq, postings_ptr]` for __apple__ while `[**e]` is for __ape__
- individual postings are only loaded and referenced from postings.txt only when the queries needs it


SEARCHING THE TREE:

- as searching for __appl__ actually returns multiple results:  `[doc_frequency, {doc_ids: [word_positions]} ]` for both __application__ and __apple__, the results are merged such that __appl__ returns the total `doc_frequency` of __application__ + __apple__ and a combined `doc_ids` + `word_positions`.
- as a result, searching for __appl__ will return all documents and corresponding positions of __application__ and __apple__, a true prefix real time search experience.

dictionary.txt
-------------
- 1st line contains the string of concatenated terms

- Subsequent lines FORMAT:
	- 1 line represents a unique term: `[doc_freq][postings_ptr][term_ptr]`  
	- `[postings_ptr]` actually refers to the corresponding line in `postings.txt`

postings.txt
------------
FORMAT:
	{ doc_id1: [list of word positions in doc_id1], doc_id2: [list of word positions in doc_id2], ... }

- 1 line represents the post-listing for 1 unique term found in the corresponding line in `dictionary.txt`

- When performing HW2 related operations such as AND OR NOT in `search.py`, only the `doc_ids` are used
- `list_of_word_positions` are reserved only for performing positional indexing.

---

Files included with this submission
---

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

- index.py <-- indexing program
- search.py <-- search program
- dictionary.txt <-- dictionary (created by index.py)
- postings.txt <-- postings (created by index.py)
- queries.txt <-- queries to execute
- output.txt <-- results (created by search.py)