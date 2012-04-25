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


class TreeNode:
	def __init__(self, name, postings=[]):
		self.name = name
		self.postings = postings
		self.children = {}
	
	def getPostings(self):
		# don't modify the node's self.postings
		all_postings = copy.deepcopy(self.postings)
		for child in self.children.itervalues():
			all_postings += child.getPostings()
		return sorted(set(all_postings))
		
	def _searchByPrefix(self, word_list):
		if len(word_list) > 0:
			char = word_list.pop(0)
			
			try:
				existingChild = self.children[char]
			except:
				existingChild = 0
				
			if existingChild:
				if len(word_list) == 0:
				# last element, get the postings
					return existingChild.getPostings()
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

	def _addWord(self, name_list, post_ids):
		if len(name_list) > 0:
			next_str = name_list.pop(0)
			
			try:
				# don't create new branch with existing nodes
				existingNode = self.children[next_str]
			except:
				existingNode = 0
			
			if existingNode:
				# last element have priority to add postings
				if len(name_list) == 0:
					existingNode.postings = post_ids
				else:
					# existingNode shall take over to continue iterate name_list
					existingNode.addWord(name_list, post_ids)
			else:
				if len(name_list) == 0:
					# last element, add postings
					self.addChild(TreeNode(next_str, post_ids))
				else:
					child = self.addChild(TreeNode(next_str))
					child._addWord(name_list, post_ids)
	# just a wrapper to pass the input as a list
	def addWord(self, word, post_ids):
		return self._addWord(list(word),post_ids)

root = TreeNode('root', [])

root.addWord('banana', [30,50])
root.addWord('ban', [20,40])
root.addWord('app', [1,3,5])
root.addWord('apple', [2,4])
root.addWord('application', [6])
root.addWord('apply', [7,8])


#debug
def getChildDetails(node, output, index=""):
	output += str(index) + "-"
	print output + node.name + " " + str(node.postings)
	for i, c in enumerate(node.children.itervalues()):
		getChildDetails(c, output, i)
getChildDetails(root, "")

# returns all postings in memory
print root.getPostings()
print root.searchByPrefix('con')