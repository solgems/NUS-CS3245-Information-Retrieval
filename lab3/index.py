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
	all_postings_list = []
	
	for doc_id in docs:
		# for positional indexes
		word_count = 1

		doc_id = int(doc_id)
		# for NOT function
		all_postings_list.append(doc_id)
		
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
						dictionary_memory[stemmed_word][doc_id].append(word_count)
					except:
						# first time this word or doc_id is appearing
						try:
							dictionary_memory[stemmed_word][doc_id] = []
							dictionary_memory[stemmed_word][doc_id].append(word_count)
						except:
							dictionary_memory[stemmed_word] = {}
							dictionary_memory[stemmed_word][doc_id] = []
							dictionary_memory[stemmed_word][doc_id].append(word_count)
				word_count+=1
				
				
	# write to the files
	# dictionary format: Freq postPointer(linenum) dictPointer(to the string)
	
	# first line is reserved for NOT operation
	postings_file.write(str(sorted(set(all_postings_list)))+ "\n")
	
	term_pos = {}
	term_len = 0
	# long single string dictionary
	for term in sorted(dictionary_memory.iterkeys()):
		dictionary_file.write(term)
		term_pos[term] = term_len
		term_len += len(term)
		
	dictionary_file.write("\n")
	
	# line number for linecache
	linenum = 2
	for term, postings in sorted(dictionary_memory.iteritems()):
		dictionary_file.write(str(len(postings)))
		postings_file.write("{")
		posting_str = ''
		for doc_id, word_pos_list in sorted(postings.iteritems()):
			posting_str += str(doc_id) + ": " + str(word_pos_list)+", "
		postings_file.write(posting_str.strip(', ') + "}\n")
		dictionary_file.write(" " + str(linenum) + " " + str(term_pos[term]) + "\n")
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