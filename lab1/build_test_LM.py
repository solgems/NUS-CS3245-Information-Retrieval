#!/usr/bin/python
import re
# import nltk
import sys
import getopt

def build_LM(in_file):
	"""
	build language models for each label
	each line in in_file contains a label and an URL separated by a tab(\t)
	"""
	print 'building language models...'
	# This is an empty method
	# Pls implement your code in below
	
	# use a dictionary as LM
	LM = {}
	
	f= file(in_file)
	for line in f:				
		# split the category and url
		(cat, url) = line.split('\t')
		
		# splice the url
		if url.startswith('http://'):
			url = url[7:]
		# pad 4 spaces in front and behind
		url = url.center(len(url)+8)

		# build the dictionary
		while len(url) > 4:
			# use the 5-gram as key for dictionary
			try:
				LM[url[:5]][cat] +=1
			except:
				# use another dictionary to store the 3 category counters
				LM[url[:5]] =  { 'Sports': 1.0, 'Arts': 1.0, 'News': 1.0}
				LM[url[:5]][cat] +=1
			# reduce the url by using the 2nd char onwards
			url = url[1:]
	f.close()
	
	# get the total count for each category for each key aka 5-gram
	total = { 'Sports': 0.0, 'Arts': 0.0, 'News': 0.0};
	for ngram in LM.iterkeys():
		for cat in LM[ngram].iterkeys():
			# total: sports, total: arts, total: news
			total[cat] += LM[ngram][cat]
	# print total
	
	# convert count to probability
	for ngram in LM.iterkeys():
		for cat in LM[ngram].iterkeys():
			LM[ngram][cat] = LM[ngram][cat]/total[cat]
			# print ngram, cat, LM[ngram][cat]

	print "language models has been built!"
	return LM
			
def test_LM(in_file, out_file, LM):
	"""
	test the language models on new URLs
	each line of in_file contains an URL
	you should print the most probable label for each URL into out_file
	"""
	print "testing language models..."
	# This is an empty method
	# Pls implement your code in below
	inFile = file(in_file)
	outFile = file(out_file,'w')
	for url in inFile:
		# save a copy
		org_url = url;
		
		# splice the url
		if url.startswith('http://'):
			url = url[7:]		
		# pad 4 spaces in front and behind
		url = url.center(len(url)+8)
		
		# reset total_prob for this line
		total_prob = {'Sports': 1.0, 'Arts': 1.0, 'News': 1.0}
		# test the model
		while len(url) > 4:
			try:
				for cat in LM[url[:5]].iterkeys():	
					total_prob[cat] *= LM[url[:5]][cat]
			except:
				pass
			# get next 5chars from url
			url = url[1:]
		
		# output the results, use the key with the maximum probability!
		outFile.write(max(total_prob, key=total_prob.get) + "\t" + org_url)
	inFile.close()
	outFile.close()

def usage():
	print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"

input_file_b = input_file_t = output_file = None
try:
	opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for o, a in opts:
	if o == '-b':
		input_file_b = a
	elif o == '-t':
		input_file_t = a
	elif o == '-o':
		output_file = a
	else:
		assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
	usage()
	sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)