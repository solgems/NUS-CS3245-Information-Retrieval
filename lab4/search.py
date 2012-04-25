import os
import re
import nltk
import sys
import getopt
from nltk import stem
import time
import copy
import math
import linecache

#number of results to return
K = 10

class QueryTerm:
	def __init__(self, name):
		self.name = name
		
# class that stores the dictionary
class DictionaryMemory:
	def __init__(self, dictionary_file, postings_file):
		self.postings_file = postings_file
		self.dictionary_mem = {}

		for line in dictionary_file:
			term, doc_freq, postings_ptr = line.strip("\n").split(' ')
			self.dictionary_mem[term] = (int(doc_freq), int(postings_ptr))
		
	def getDocFreq(self, term):
		# (doc_freq, postings_ptr)
		return self.dictionary_mem[term][0]
		
	def getPostings(self, term):
		postings_ptr = self.dictionary_mem[term][1]
		return eval(linecache.getline(postings_file, postings_ptr))
		
	def getNumDocs(self):
		return len(self.dictionary_mem)
		
	def exists(self, term):
		return term in self.dictionary_mem
		
# main function
def perform_search(dictionary_file, postings_file, queries_file, results_file):
	# load the dictionary file to memory (hash table)
	dictionary_mem = DictionaryMemory(file(dictionary_file), postings_file)

	queries_file = file(queries_file)
	results_file = file(results_file, 'w')
	stemmer = stem.PorterStemmer()
	
	# a cache for holding terms that appeared recently
	all_query_terms_cache = {}
	
	# for handling multiple lines of queries
	for queryline in queries_file:
	
		scores = {}
		query_vector = []
		
		# list of query terms
		original_query_terms_list = queryline.strip(' ').strip('\n').split(' ')
		# replace the original query terms with stemmed terms
		for query_term in original_query_terms_list:
			stemmed_term = stemmer.stem(query_term)
			stemmed_term = stemmed_term.lower()
			original_query_terms_list[original_query_terms_list.index(query_term)] = stemmed_term
		
		# have a new list without repeating the same stemmed_term
		query_terms_list = list(set(original_query_terms_list))

		# convert each query_term (STRING) in query_terms_list to QueryTerm (object)
		for query_term in query_terms_list:
		
			# don't process for terms that does not exist in dictionary
			if (dictionary_mem.exists(query_term)):
				if (query_term in all_query_terms_cache):
					# term already exists in memory, no need to traverse dictionary again
					term_obj = copy.deepcopy(all_query_terms_cache[query_term])
				else:
					# new term
					term_obj = QueryTerm(query_term)
					# search and get from dictionary_mem
					term_obj.doc_freq = dictionary_mem.getDocFreq(term_obj.name)
					term_obj.postings = dictionary_mem.getPostings(term_obj.name)
					term_obj.idf = math.log( (dictionary_mem.getNumDocs()/term_obj.doc_freq) , 10)
					# add it to memory for resuability
					all_query_terms_cache[query_term] = term_obj
				
				# calculate weight for this query term
				# tf
				query_tf = original_query_terms_list.count(query_term)
				# tf-wt (log)
				query_tf_wt = 1 + math.log(query_tf, 10)
				# tf-idf (ltc)
				query_tf_idf = query_tf_wt * term_obj.idf
				
				# for normalizing
				query_vector.append(query_tf_idf)
				
				# process all doc's tf-idf for this term
				for doc in term_obj.postings:
					# doc[0] -> doc_id, doc[1] = doc_tf
					# doc uses lnn notation
					doc_tf_idf = 1 + math.log(doc[1], 10)
					try:
						scores[doc[0]] += query_tf_idf * doc_tf_idf
					except:
						# document first time appearing
						scores[doc[0]] = query_tf_idf * doc_tf_idf
		
		# for normalizing query vector
		# feels useless by only normalizing the query as it's a constant for all docs
		# but still included it here since it's lnn.ltc not lnn.ltn
		sum_query_wt = 0
		for wt in query_vector:
			sum_query_wt += wt*wt
		query_vector_length = math.sqrt(sum_query_wt)
		
		for doc, score in scores.iteritems():
			# normalize
			scores[doc] = score/query_vector_length
			
		
		i = 0
		results_str = ''
		# sorted by descending value(score) then ascending key for same scores(docid)
		for key, value in sorted(scores.items(), key=lambda x: (-1*x[1], x[0])):
			# print "%s: %s" % (key, value)
			if (i < K):
				results_str += str(key) + ' '
				i+= 1
		results_file.write(results_str.strip(' ')+"\n")
	results_file.close()
	
def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

dictionary_file = postings_file = queries_file = results_file = None;
try:
	opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for opt, a in opts:
	if opt == '-d':
		dictionary_file = a
	elif opt == '-p':
		postings_file = a
	elif opt == '-q':
		queries_file = a
	elif opt == '-o':
		results_file = a
	else:
		assert False, "unhanded option"
if dictionary_file == None or postings_file == None or queries_file == None or results_file == None:
	usage()
	sys.exit(2)

perform_search(dictionary_file, postings_file, queries_file, results_file)

# commands
# python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt