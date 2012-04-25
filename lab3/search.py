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

class QueryTerm:
	def __init__(self, name):
		self.name = name

# data structure used by memory tree
class TreeNode:
	def __init__(self, name, lists=[]):
		self.name = name
		self.lists = lists
		self.children = {}
		
	def combineList(self, list1, list2):
		if list1 == []:
			return list2
		if list2 == []:
			return list1
		return [list1[0]+list2[0], list1[1]+list2[1]]
		
	def getList(self):
		# care to not modify the node's original self.list
		all_lists = copy.deepcopy(self.lists)
		for child in self.children.itervalues():
			all_lists = self.combineList(all_lists,child.getList())
		return all_lists
	
	# main searching method
	def _searchByPrefix(self, word_list):
		if len(word_list) > 0:
			char = word_list.pop(0)
			
			try:
				existingChild = self.children[char]
			except:
				existingChild = 0
				
			if existingChild:
				if len(word_list) == 0:
				# last element, get the lists
					return existingChild.getList()
				else:
					return existingChild._searchByPrefix(word_list)
			else:
				return []
	
	# just a wrapper to pass the input as a list
	def searchByPrefix(self, word):
		return self._searchByPrefix(list(word))

	def addChild(self, newNode):
		self.children[newNode.name] = newNode
		return newNode

	# method to add new word to tree
	def _addWord(self, name_list, listItems):
		if len(name_list) > 0:
			next_str = name_list.pop(0)
			
			try:
				# don't create new branch with existing nodes
				existingNode = self.children[next_str]
			except:
				existingNode = 0
			
			if existingNode:
				# last element have priority to add lists
				if len(name_list) == 0:
					existingNode.lists = listItems
				else:
					# existingNode shall take over to continue iterate name_list
					existingNode.addWord(name_list, listItems)
			else:
				if len(name_list) == 0:
					# last element, add lists
					self.addChild(TreeNode(next_str, listItems))
				else:
					child = self.addChild(TreeNode(next_str))
					child._addWord(name_list, listItems)

	# just a wrapper to pass the input as a list
	def addWord(self, word, listItems):
		return self._addWord(list(word),listItems)

# class that stores the tree
class DictionaryMemoryTree:
	def __init__(self, dictionary_file, postings_file):
		self.postings_file = postings_file
		
		# load whole file into a buffer list first
		# buffer_list = [freq, postings_ptr, term_ptr]
		buffer_list = []
		got_all_terms_flag = 0
		for line in dictionary_file:
			# first line contains all terms
			if not got_all_terms_flag:
				all_terms_string = line
				got_all_terms_flag = 1
			else:
				freq, postings_ptr, term_ptr = line.strip("\n").split(' ')
				buffer_list.append([int(freq), int(postings_ptr), int(term_ptr)])
				
		
		# transfer into tree to allow prefix searches
		# root.getList(term_name) = [freq, postings_ptr]
		self.root = TreeNode('root')
		for i in range(len(buffer_list)):
			dictionary_file.seek(buffer_list[i][2],0)
			try:
				term_name = dictionary_file.read(buffer_list[i+1][2] - buffer_list[i][2])
			except:
				# read the rest of the line as we don't know how many bytes to read
				term_name = dictionary_file.readline().strip("\n")
			
			# [combined_doc_freq, lists of linenums]
			self.root.addWord(term_name, [ buffer_list[i][0], [buffer_list[i][1]] ] )

		
	def getDocFreq(self, term_name):
		docFreq = 0
		try:
			docFreq = self.root.searchByPrefix(term_name)[0]
		except:
			print "docFreq of term '"+ term_name + "' not found"
		return docFreq
	
	# custom method to combine 2 positional positing lists
	def combinePostingsDics(self, dic1, dic2):
		if dic1 == {}:
			return dic2
		if dic2 == {}:
			return dic1
		result = dic1
		for key2, list2 in dic2.iteritems():
			try:
				# same key exist, combine the lists
				result[key2] += list2
				result[key2] = sorted(set(result[key2]))
			except:
				result[key2] = list2
		return result
	
	def getPostings(self, term_name):
		postings = {}
		list_of_ptrs = []
		try:
			list_of_ptrs = self.root.searchByPrefix(term_name)[1]
		except:
			print "postings of term '"+ term_name + "' not found"

		# need to get from multiple lines and merge if there are multiple results found
		for posting_ptr in list_of_ptrs:
			postings = self.combinePostingsDics(postings, eval(linecache.getline(postings_file, posting_ptr)))
		return postings

class ShuntOp:
	def __init__(self, name):
		# higher precedence is higher priority
		self.name = name
		if (name == 'AND'):
			self.assoc_dir = 'LEFT'
			self.precedence = 2
		elif (name == '+'):
			self.assoc_dir = 'LEFT'
			self.precedence = 3
		elif (name == 'OR'):
			self.assoc_dir = 'LEFT'
			self.precedence = 1
		elif (name == 'NOT'):
			self.assoc_dir = 'RIGHT'
			self.precedence = 4

# accepts a list of tokens
# shunting-yard-algorithm
def infix_to_postfix(infix):
	output_queue = []
	operator_stack = []
	while (len(infix) > 0):
		token = infix.pop(0)
		if ((token == 'AND') | (token == '+') | (token == 'OR') | (token == 'NOT')):
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

# "APPLE PEAR ORANGE" is converted to APPLE + PEAR + ORANGE
def parseQuotesToPlus(query_terms_list):
	# remove the spaces
	while query_terms_list.count('') > 0:
		query_terms_list.remove('')
	
	# replace terms inside quotes with +
	while query_terms_list.count('"') > 0:
		quote_pos = query_terms_list.index('"')
		query_terms_list.pop(quote_pos)
		
		while query_terms_list[quote_pos+1] != '"':
			query_terms_list.insert(quote_pos+1, '+')
			quote_pos += 2
		# remove closing quote
		quote_pos = query_terms_list.index('"')
		query_terms_list.pop(quote_pos)
	
	return query_terms_list

# AND, + operations
# skipping of posts added to speed up comparison
def intersect(postings1, postings2, positional):
	doc_ids1 = sorted(postings1)
	doc_ids2 = sorted(postings2)
	answer = []
	jump_factor_p1 = int(round(math.sqrt(len(doc_ids1))))
	jump_factor_p2 = int(round(math.sqrt(len(doc_ids2))))
	
	while ( (len(doc_ids1) > 0) & (len(doc_ids2) > 0) ):
		if (doc_ids1[0] == doc_ids2[0]):
			answer.append(doc_ids1[0])
			next1 = doc_ids1.pop(0)
			next2 = doc_ids2.pop(0)
			
			if (next1 < next2):
				if (len(doc_ids1) > jump_factor_p1):
					if (doc_ids1[jump_factor_p1] < next2):
						doc_ids1 = doc_ids1[jump_factor_p1:]
			elif (next2 < next1):
				if (len(doc_ids2) > jump_factor_p2):
					if (doc_ids2[jump_factor_p2] < next1):
						doc_ids2 = doc_ids2[jump_factor_p2:]
			
		elif (doc_ids1[0] < doc_ids2[0]):
			next = doc_ids1.pop(0)
			
			if (next < doc_ids2[0]):
				if (len(doc_ids1) > jump_factor_p1):
					if (doc_ids1[jump_factor_p1] < doc_ids2[0]):
						doc_ids1 = doc_ids1[jump_factor_p1:]
		else:
			next = doc_ids2.pop(0)
			
			if (next < doc_ids1[0]):
				if (len(doc_ids2) > jump_factor_p2):
					if (doc_ids2[jump_factor_p2] < doc_ids1[0]):
						doc_ids2 = doc_ids2[jump_factor_p2:]
						
	# additional steps for positional indexing
	if (positional):
		positional_answer = {}
		for common_doc in answer:
			word_pos_list1 = postings1[common_doc]
			word_pos_list2 = postings2[common_doc]
			
			while (len(word_pos_list1) > 0 ) & (len(word_pos_list2) > 0):
				if (word_pos_list1[0]+1 == word_pos_list2[0]):
					try:
						positional_answer[common_doc].append(word_pos_list2[0])
					except:
						positional_answer[common_doc] = []
						positional_answer[common_doc].append(word_pos_list2[0])
					word_pos_list1.pop(0)
					word_pos_list2.pop(0)
				elif (word_pos_list1[0]+1 < word_pos_list2[0]):
					word_pos_list1.pop(0)
				else:
					word_pos_list2.pop(0)
		return positional_answer
	else:
		return answer

# OR operation
def join(postings1, postings2):
	# set makes it unique values only
	answer = sorted(list(set(list(postings1) + list(postings2))))
	return answer

# NOT operation
def invert(postings):
	# first line contains list of all postings
	all_postings = eval(linecache.getline(postings_file, 1))
	answer = list(set(all_postings) - set(list(postings)))
	return answer

# go through the query stack and get the results
def evaluate_postfix_stack(query_terms_list):
	#evaulate the postfix stack
	eval_stack = []
	while (len(query_terms_list) > 0):
		x = query_terms_list.pop(0)
		
		# if term
		if (x.__class__.__name__ == 'QueryTerm'):
			# some terms have no postings
			if (hasattr(x, 'postings')):
				eval_stack.append(x.postings)
			else:
				eval_stack.append([])
		else:
			# it is a operator
			if ((x.name == '+') | (x.name == 'AND') | (x.name == 'OR')):		
				op1 = eval_stack.pop()
				op2 = eval_stack.pop()
				if (x.name == '+'):
					eval_stack.append(intersect(op2,op1,1))				
				elif (x.name == 'AND'):
					eval_stack.append(intersect(op2,op1,0))
				elif (x.name == 'OR'):
					eval_stack.append(join(op2,op1))
			else:
				# it must be a NOT
				op1 = eval_stack.pop()
				eval_stack.append(invert(op1))
				
	return eval_stack.pop()


# main function
def perform_search(dictionary_file, postings_file, queries_file, results_file):
	# load the dictionary file to memory (tree structure)
	dictionary_mem_tree = DictionaryMemoryTree(file(dictionary_file), postings_file)
	
	queries_file = file(queries_file)
	results_file = file(results_file, 'w')
	stemmer = stem.PorterStemmer()
	
	# a cache for holding terms that appeared recently
	all_query_terms = {}
	
	# for handling multiple lines of queries
	for queryline in queries_file:
		query_terms_list = []
		# to handle the parenthesis syntax correctly
		# end result is with a space,"smth AND ( smth OR smth ) AND smth"
		queryline = queryline.replace('( ', '(')
		queryline = queryline.replace(' )', ')')
		queryline = queryline.replace('(', '( ')
		queryline = queryline.replace(')', ' )')
		
		queryline = queryline.replace(' "', '"')
		queryline = queryline.replace('" ', '"')
		queryline = queryline.replace('"',' " ')
		queryline = queryline.replace('  ',' ')
		query_terms_list = queryline.strip('\n').split(' ')
		
		query_terms_list = parseQuotesToPlus(query_terms_list)
		
		# convert to postfix
		# operators will be converted to ShuntOp objects
		query_terms_list = infix_to_postfix(query_terms_list)

		# convert each query_term (STRING) in query_terms_list to QueryTerm (object)
		for query_term in query_terms_list:
			if (query_term.__class__.__name__ != 'ShuntOp'):
				
				stemmed_term = stemmer.stem(query_term)
				stemmed_term = stemmed_term.lower()
			
				if (stemmed_term in all_query_terms):
					# term already exists in memory, no need to traverse dictionary again
					query_terms_list[query_terms_list.index(query_term)] = copy.deepcopy(all_query_terms[stemmed_term])
				else:
					# new term
					term_obj = QueryTerm(stemmed_term)
					# search and get from tree
					term_obj.doc_freq = dictionary_mem_tree.getDocFreq(term_obj.name)
					term_obj.postings = dictionary_mem_tree.getPostings(term_obj.name)
					# add it to memory
					all_query_terms[stemmed_term] = term_obj
					# convert string to term_obj in query_terms_list
					query_terms_list[query_terms_list.index(query_term)] = copy.deepcopy(all_query_terms[stemmed_term])
			
		# evaluate the postfix query
		result_list = evaluate_postfix_stack(query_terms_list)
		# convert hashtable to list
		result_list = sorted(set(result_list))
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

perform_search(dictionary_file, postings_file, queries_file, results_file)

# commands
# python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt