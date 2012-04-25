import sys
import getopt
import linecache

def calculate(gold_standard_file, prediction_file, line_number, results_file):
	results_fh = file(results_file, 'w')

	# gold list
	gold_list_str = linecache.getline(gold_standard_file, line_number).split(' ')
	gold_list = [int(x) for x in gold_list_str]

	# output list
	predict_list_str = linecache.getline(prediction_file, line_number).split(' ')
	predict_list = [int(x) for x in predict_list_str]

	# list of the ranks
	rank_hash = []

	retrieved = 0
	relevant_retrieved = 0
	relevant = len(gold_list)
	for predict in predict_list:
		results = {}
		retrieved += 1
		if predict in gold_list:
			relevant_retrieved += 1

		# calculate precision and recall
		try:
			results['precision'] = round( (relevant_retrieved * 100.0 / retrieved), 2)
		except:
			results['precision'] = 0.0
		try:
			results['recall'] = round( (relevant_retrieved * 100.0 / relevant), 2)
		except:
			results['recall'] = 0.0

		rank_hash.append(results)

	# interpolate the results
	# assuming that recall is always same or increasing, we start from the back
	rank_hash.reverse()

	max_precision = 0.0
	for rank in rank_hash:
		max_precision = max(max_precision, rank['precision'])
		rank['precision'] = max_precision

		# calculate F1 using interpolated precision
		try:
			rank['F1'] = round( (2 * (rank['precision'] * rank['recall']) 
								/ (rank['precision'] + rank['recall']) ) ,2)
		except:
			rank['F1'] = 0.0

	# which back for printing
	rank_hash.reverse()

	for i, rank in enumerate(rank_hash):
		results_fh.write("Precision at Rank %s: %s\n"  % (i+1, rank['precision']) )
		results_fh.write("Recall at Rank %s: %s\n" % (i+1, rank['recall']))
		results_fh.write("F1 at Rank %s: %s\n" % (i+1, rank['F1']))


	results_fh.close()

def usage():
	print "usage: " + sys.argv[0] + " -l line-number -g correct-file-of-results -p output-file-of-results -o output-statistics.txt"

gold_standard_file = prediction_file = results_file = line_number = None
try:
	opts, args = getopt.getopt(sys.argv[1:], 'g:p:l:o:')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for o, a in opts:
	if o == '-g':
		gold_standard_file = a
	elif o == '-p':
		prediction_file = a
	elif o == '-l':
		line_number = a
	elif o == '-o':
		results_file = a
	else:
		assert False, "unhanded option"

if gold_standard_file == None or prediction_file == None or results_file == None or line_number == None:
	usage()
	sys.exit(2)

calculate(gold_standard_file, prediction_file, int(line_number), results_file)

# commands
# python eval-ir.py -l 1 -g correct-file-of-results -p output-file-of-results -o output-statistics.txt