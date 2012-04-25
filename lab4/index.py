import os
import re
import nltk
import sys
import getopt
from nltk import stem

def build_index(reuters_dir, dictionary_file, postings_file):
	# init
	dictionary_file = file(dictionary_file,'w')
	postings_file = file(postings_file,'w')
	stemmer = stem.PorterStemmer()
	docs = os.listdir(reuters_dir)
	
	# to store the dictionary in memory using dictionary(datatype)
	# so we can have unique entries only
	dictionary_memory = {}
	
	for doc_id in docs:
		doc_id = int(doc_id)
		
		fh = open(reuters_dir+"/"+str(doc_id))
		text = fh.read()
		text = re.sub('\n', ' ', text)
		text = re.sub(' +', ' ', text)
		for sentence in nltk.sent_tokenize(text):
			for word in nltk.word_tokenize(sentence):
				# alphanumeric only, ignore pure punctuations
				if (re.search('\w',word)):
					# convert to lower, stem the word
					stemmed_word = stemmer.stem(word.lower())
					# populate our memory
					try:
						# calculate the term-freq of this word in this doc_id
						dictionary_memory[stemmed_word][doc_id] += 1
					except:
						# first time this word or doc_id is appearing
						try:
							dictionary_memory[stemmed_word][doc_id] = 1
						except:
							dictionary_memory[stemmed_word] = {}
							dictionary_memory[stemmed_word][doc_id] = 1	
				
	# write to the files
	# dictionary format: term doc-freq postPointer(linenum)
	
	# line number for linecache
	linenum = 1
	for term, postings in sorted(dictionary_memory.iteritems()):
		# write the doc-freq (no. of docs) for this term
		dictionary_file.write(term + " " + str(len(postings)) + " " + str(linenum) + "\n")
		postings_file.write("[")
		posting_str = '' 
		for doc_id, term_freq in sorted(postings.iteritems()):
			posting_str += "(" + str(doc_id) + "," + str(term_freq)+"), "			
		postings_file.write(posting_str.strip(', ') + "]\n")
		linenum += 1
	dictionary_file.close()
			
def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

directory_of_documents = dictionary_file = postings_file = None
try:
	opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for o, a in opts:
	if o == '-i':
		directory_of_documents = a
	elif o == '-d':
		dictionary_file = a
	elif o == '-p':
		postings_file = a
	else:
		assert False, "unhanded option"
if directory_of_documents == None or dictionary_file == None or postings_file == None:
	usage()
	sys.exit(2)

index = build_index(directory_of_documents, dictionary_file, postings_file)



# commands
# python index.py -i ~/nltk_data/corpora/reuters/training/ -d dictionary.txt -p postings.txt
# python index.py -i ~/nltk_data/corpora/reuters/training_subset/ -d dictionary.txt -p postings.txt