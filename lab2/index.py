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
		doc_id = int(doc_id)
		# for NOT function
		all_postings_list.append(doc_id)
		
		text = open(reuters_dir+"/"+str(doc_id))
		sentence_list = nltk.sent_tokenize(text.read())
		for sentence in sentence_list:
			word_list = nltk.word_tokenize(sentence)
			for word in word_list:
				# alphanumeric only, ignore pure punctuations					
				if (re.search('\w',word)):
					# stem the word
					stemmed_word = stemmer.stem(word)
					# convert to lower
					stemmed_word = stemmed_word.lower()
					# populate our memory
					try:
						# we don't need repeating doc_ids
						if (doc_id not in dictionary_memory[stemmed_word]):
							# key already exist, append value:doc instead of overwriting
							dictionary_memory[stemmed_word].append(doc_id)
					except:
						# key does not exist
						dictionary_memory[stemmed_word] = []
						dictionary_memory[stemmed_word].append(doc_id)
	
	# pointer to the postings for f.seek()
	pointer_pos = 0;
	len_posting = 0;
	for key,postings in dictionary_memory.iteritems():
		
		postings.sort()
		num_bytes = len(str(postings).replace(' ', '')) - 1
		# key, doc_freq, ptr_pos, num_bytes(number of bytes to read)
		dictionary_file.write(key + " " + str(len(postings)) + " " + str(pointer_pos) + " " + str(num_bytes) + "\n")
		for i in range(0,len(postings)):
			if (i < len(postings)-1):
				postings_file.write(str(postings[i]) + ",")
			else:
				# last element of each line
				postings_file.write(str(postings[i])+ "\n")		
		pointer_pos += num_bytes
	
	# for NOT function
	len_all_postings = len(str(all_postings_list).replace(' ', '').strip('[').strip(']'))
	dictionary_file.write("_ALLPOSTINGS_ " + str(len(all_postings_list)) + " " + str(pointer_pos) + " " + str(len_all_postings))
	postings_file.write(str(sorted(all_postings_list)).replace(' ','').strip('[').strip(']'))
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