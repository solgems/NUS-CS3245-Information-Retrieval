import os
import re
import nltk
import sys
import getopt
from nltk import stem
import time
import copy
import math

class ShuntOp:
	def __init__(self, name):
		self.name = name
		if (name == 'AND'):
			self.assoc_dir = 'LEFT'
			self.precedence = 2
		elif (name == 'OR'):
			self.assoc_dir = 'LEFT'
			self.precedence = 1
		elif (name == 'NOT'):
			self.assoc_dir = 'RIGHT'
			self.precedence = 3
			

# accepts a list of tokens
# shunting-yard-algorithm
def infix_to_postfix(infix):
	output_queue = []
	operator_stack = []
	while (len(infix) > 0):
		token = infix.pop(0)
		if ((token == 'AND') | (token == 'OR') | (token == 'NOT')):
			# operator
			op = ShuntOp(token)
			try:
				while (operator_stack[-1].__class__.__name__ == 'ShuntOp'):
					if ( ((op.assoc_dir == 'LEFT') & (op.precedence <= operator_stack[-1].precedence)) |	\
						((op.assoc_dir == 'RIGHT') & (op.precedence < operator_stack[-1].precedence)) ):
						output_queue.append(operator_stack.pop())
					else: break
			except: pass
			operator_stack.append(op)
		elif (token == '('):
			operator_stack.append(token)
		elif (token == ')'):
			while (operator_stack[-1]!= '('):
				output_queue.append(operator_stack.pop())
			operator_stack.pop()			
		else:
			# word
			output_queue.append(token)
		
	# after no more tokens to read
	while (len(operator_stack) > 0 ):
		output_queue.append(operator_stack.pop())
		
	return output_queue

			
class QueryTerm:
	def __init__(self, name):
		self.name = name
		
	# retrieve the postings
	def getPostings(self, postings_file):
		postings_file.seek(self.ptr_pos, 0)
		# read in 1 line from postings_file
		postings = postings_file.read(int(self.num_bytes))
		# remove the \n behind and commas and add each individual post to a list
		splitted = postings.strip('\n').split(',')
		# a new post-listing
		splitted_int = []
		for l in splitted:
			splitted_int.append(int(l))
			
		self.postings = splitted_int
		return self.postings


# intersect postings
# skipping of posts added to speed up comparison
def intersect(postings1, postings2):
	answer = []
	jump_factor_p1 = int(round(math.sqrt(len(postings1))))
	jump_factor_p2 = int(round(math.sqrt(len(postings2))))
	
	while ( (len(postings1) > 0) & (len(postings2) > 0) ):
		if (postings1[0] == postings2[0]):
			answer.append(postings1[0])
			next1 = postings1.pop(0)
			next2 = postings2.pop(0)
			
			if (next1 < next2):
				if (len(postings1) > jump_factor_p1):
					if (postings1[jump_factor_p1] < next2):
						postings1 = postings1[jump_factor_p1:]
			elif (next2 < next1):
				if (len(postings2) > jump_factor_p2):
					if (postings2[jump_factor_p2] < next1):
						postings2 = postings2[jump_factor_p2:]
			
		elif (postings1[0] < postings2[0]):
			next = postings1.pop(0)
			
			if (next < postings2[0]):
				if (len(postings1) > jump_factor_p1):
					if (postings1[jump_factor_p1] < postings2[0]):
						postings1 = postings1[jump_factor_p1:]
		else:
			next = postings2.pop(0)
			
			if (next < postings1[0]):
				if (len(postings2) > jump_factor_p2):
					if (postings2[jump_factor_p2] < postings1[0]):
						postings2 = postings2[jump_factor_p2:]
	return answer

# merge postings
def join(postings1, postings2):
	# set makes it unique values only
	answer = sorted(list(set(postings1 + postings2)))
	return answer

# NOT operation
def invert(all_postings, postings):
	answer = list(set(all_postings) - set(postings))
	return answer


def perform_search(dictionary_file, postings_file, queries_file, results_file):
	# init
	dictionary_file = file(dictionary_file)
	postings_file = file(postings_file)
	queries_file = file(queries_file)
	results_file = file(results_file, 'w')
	stemmer = stem.PorterStemmer()
	
	# build an object that consists of all postings for NOT operation
	allpostings_obj = QueryTerm('_ALLPOSTINGS_')
	dictionary_lines = dictionary_file.readlines()
	(key, doc_freq, ptr_pos, num_bytes) = dictionary_lines[-1].split(' ')
	allpostings_obj.doc_freq = int(doc_freq)
	allpostings_obj.ptr_pos = int(ptr_pos)
	allpostings_obj.num_bytes = int(num_bytes)
	allpostings_obj.getPostings(postings_file)
	# rewind
	dictionary_file.seek(0)
	
	# a cache for holding terms that appeared recently
	all_query_terms = {}
	for query in queries_file:
		query_terms = []
		# to handle the parenthesis syntax correctly
		query = query.replace('( ', '(')
		query = query.replace('(', '( ')
		query = query.replace(' )', ')')
		query = query.replace(')', ' )')
		query_terms = query.strip('\n').split(' ')
		
		# reorder to postfix
		# operators will be converted to ShuntOp objects
		query_terms = infix_to_postfix(query_terms)

		# process each term in the query
		for query_term in query_terms:
			if (query_term.__class__.__name__ != 'ShuntOp'):
				
				stemmed_term = stemmer.stem(query_term)
				stemmed_term = stemmed_term.lower()
			
				if (stemmed_term in all_query_terms):
					# term already exists in memory, no need to traverse dictionary again
					query_terms[query_terms.index(query_term)] = copy.deepcopy(all_query_terms[stemmed_term])
				else:
					# new term
					term_obj = QueryTerm(stemmed_term)
					
					# traverse the dictionary_file
					for line in dictionary_file:
						# get the term doc_freq, ptr_pos and num_bytes
						# asume unique term, only returns 1 result
						# search for whole word only
						if (re.match(term_obj.name+' ', line) ):
							(key, doc_freq, ptr_pos, num_bytes) = line.split(' ')
							term_obj.doc_freq = int(doc_freq)
							term_obj.ptr_pos = int(ptr_pos)
							term_obj.num_bytes = int(num_bytes)
							term_obj.getPostings(postings_file)
					
					# add it to memory
					all_query_terms[stemmed_term] = term_obj
					# convert string to term_obj
					query_terms[query_terms.index(query_term)] = copy.deepcopy(all_query_terms[stemmed_term])
					# rewind
					dictionary_file.seek(0)
		
		#evaulate the postfix stack
		eval_stack = []
		while (len(query_terms) > 0):
			x = query_terms.pop(0)
			
			# if term
			if (x.__class__.__name__ == 'QueryTerm'):
				# some terms have no postings
				if (hasattr(x, 'postings')):
					eval_stack.append(x.postings)
				else:
					eval_stack.append([])
			else:
				# it is a operator
				if ((x.name == 'AND') | (x.name == 'OR')):		
					op1 = eval_stack.pop()
					op2 = eval_stack.pop()					
					if (x.name == 'AND'):
						eval_stack.append(intersect(op2,op1))
					elif (x.name == 'OR'):
						eval_stack.append(join(op2,op1))
				else:
					# it must be a NOT
					op1 = eval_stack.pop()
					eval_stack.append(invert(allpostings_obj.postings, op1))
	
		result_list = eval_stack.pop()
		results_file.write(str(result_list).strip('[').strip(']').replace(',','')+"\n")
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

start = time.time()
perform_search(dictionary_file, postings_file, queries_file, results_file)
print time.time()-start


# commands
# python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt