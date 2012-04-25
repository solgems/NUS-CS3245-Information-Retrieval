import sys
import getopt

def calculate(gold_standard_file, prediction_file, classes_file, results_file):
	classes_fh = open(classes_file)
	results_fh = file(results_file, 'w')

	# first level for the class_name
	results_hash = {}

	for class_name in classes_fh:
		class_name = class_name.strip('\n')
		results_hash[class_name] = {}
		calculate_class(gold_standard_file, prediction_file, class_name, results_hash[class_name])

	total_precision = 0
	total_recall = 0
	total_f1 = 0
	for class_name in results_hash:
		results_fh.write("Precision of %s: %s\n" % (class_name, results_hash[class_name]['precision']) )
		results_fh.write("Recall of %s: %s\n" % (class_name, results_hash[class_name]['recall']) )
		results_fh.write("F1 of %s: %s\n" % (class_name, results_hash[class_name]['F1']) )

		# for average
		total_precision += results_hash[class_name]['precision']
		total_recall += results_hash[class_name]['recall']
		total_f1 += results_hash[class_name]['F1']

	# len(results_hash) returns number of classes
	results_fh.write("Average Precision: %s\n"  % (float(total_precision) / len(results_hash)) )
	results_fh.write("Average Recall: %s\n" % (float(total_recall) / len(results_hash)) )
	results_fh.write("Average F1: %s\n" % (float(total_f1) / len(results_hash)) )
	results_fh.close()

def calculate_class(gold_standard_file, prediction_file, class_name, results_class):

	gold_standard_fh = open(gold_standard_file)
	prediction_fh = open(prediction_file)
	relevant = 0
	retrieved = 0
	relevant_retrieved = 0
	
	for line1 in prediction_fh:
		line2 = gold_standard_fh.readline()
		res1 = line1.split()[0]
		res2 = line2.split()[0]

		if res1 == class_name:
			retrieved += 1
		if res2 == class_name:
			relevant +=1
		if (res1 == res2) and (res1 == class_name) and (res2 == class_name):
			relevant_retrieved += 1

	prediction_fh.close()
	gold_standard_fh.close()

	# set division by 0 to 0
	try:
		results_class['precision'] = round( (relevant_retrieved * 100.0 / retrieved), 2)
	except:
		results_class['precision'] = 0.0
	try:
		results_class['recall'] = round( (relevant_retrieved * 100.0 / relevant), 2)
	except:
		results_class['recall'] = 0.0
	try:
		results_class['F1'] = round( (2 * (results_class['precision'] * results_class['recall']) 
									/ (results_class['precision'] + results_class['recall']) ) ,2)
	except:
		results_class['F1'] = 0.0

	return results_class


def usage():
	print "usage: " + sys.argv[0] + " -g urls.correct.txt -p urls.predict.txt -c classes.txt -o output-statistics.txt"

gold_standard_file = prediction_file = classes_file = results_file = None
try:
	opts, args = getopt.getopt(sys.argv[1:], 'g:p:c:o:')
except getopt.GetoptError, err:
	usage()
	sys.exit(2)
for o, a in opts:
	if o == '-g':
		gold_standard_file = a
	elif o == '-p':
		prediction_file = a
	elif o == '-c':
		classes_file = a
	elif o == '-o':
		results_file = a
	else:
		assert False, "unhanded option"

if gold_standard_file == None or prediction_file == None or classes_file == None or results_file == None:
	usage()
	sys.exit(2)

calculate(gold_standard_file, prediction_file, classes_file, results_file)

# commands
# python eval-c.py -g urls.correct.txt -p urls.predict.txt -c classes.txt -o output-statistics.txt