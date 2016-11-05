#------------------------------------------------------------------
'''
#------------------------------------------------------------------
# This code thankfully acknowledges the python from the book
# "Mining the Social Web " (2nd Edition) by M. Russel
# and the tutorials by Harrison on the youtube channel "sentdex"
# this code developed by daniel phillis
# SID 2110633, FAN phil0411
# with the help mentioned above

#------------------------------------------------------------------
# Summary
# you can now specify a path as an argument
# to point the sciript to a particular bunch of files
# ie run_my_script.py --path ../../wierd_directory/my_tweet_data.txt
# 
# the default path the pwd "./"
# the script will LOOP OVER ALL text files in the target directory 
# and parse them for keywords representing positive and negative 
# sentiment (which are hardcoded in this script)

# the file path can and currently being stripped off so that results are easily found
# - they are written to files in the same directory as the script's location when run

# only text files are parsed (with .txt extension) other files are ignored
# see "### FILE EXTENSION FILTER"
# result values are normalised over the total number of words parsed.

# the args pos or neg can be passed to the python command 
# to activate either the pos or neg array of keywords
# the default is positive

# in consideration for next version
# reading keywords from disk

# adjective functionality currently commented out
'''

import decimal #for rounding values before writing to csv

import sys
import time
import datetime
import twitter
import io
import os
from os import listdir
from os.path import isfile, join

import csv
from prettytable import PrettyTable

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from prettytable import PrettyTable
from collections import Counter

import argparse
parser = argparse.ArgumentParser(description='Short sample app')
# Declare an argument (`--algo`), telling that the corresponding value should be stored in the `algo` field, and using a default value if the argument isn't given

#specific path arg
parser.add_argument('--p', action="store", dest='path', 
	default='./')

#sentiment toggle
parser.add_argument('--s', action="store", dest='sent',
	default='pos')

# parse the command line arguments and store the values in the `args` variable
args = parser.parse_args()
# Individual arguments can be accessed as attributes...
# ie #print("default path arg:" + args.path)

#------------------------------------------------------------------
def analyse_content(data, keywords, size, entityThreshold=3):
	if len(data) == 0:
		print("No data to analyze")
		return

	stop_Words = stopwords.words("english")
	#camel case convention is broken to accentuate custom var over nltk module 'stopwords'

	customStopWords = [
						"Galaxy","Samsung","Note","replies","retweets",
						"Retweet","Reply","Edge","http","iPhone","S7","7",
						"Sep","More","Like","Aug"]

	punc = ["-",":","...","@","#",".",",","?"]
	#nums = ["1","2","3","4","5","6","7","8","9","0"," ","\t","\t\t"]
	# word tokenize should handle numbers for us

	stop_Words += customStopWords
	stop_Words += punc

	size = 10
	c = Counter(data).most_common(size)
	# Compute frequencies *with a dictionary (tuples)
	tups = [ (k,v) for (k,v) in c if v >= entityThreshold and k not in stop_Words]

	#print tups #debug

	#pt is suitable for console display but not for writing a csv to disk
	'''
	pt = PrettyTable(field_names=['Entity', 'Count'])	
	[ pt.add_row(kv) for kv in tups ]
	pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment
	print pt
	'''
	# for each item in the keywords dict, count the re-occurances
	for w in data:
		for k in keywords:
			if ('' +k) in ('' + w):
				keywords[k] = keywords[k] + 1 #increase the value of key k
				pass
	
	#print "keywords"
	#print keywords #prints each word to a new line	
	return keywords#dictionary
#------------------------------------------------------------------    

def stripPath(fileName):
	print("stripping path...")
	
	#strip readPath and return just the fileName
	oldPath = fileName.split("/")

	#print("old file path,Name: " + str(oldPath) + " " + str(fileName))	
	print("old file path,Name: " + str(fileName))	
	pathSize = len(oldPath)
	fileName = oldPath[pathSize-1]

	#strip txt extension
	flen = len(fileName)	#print(fileName[:fl-1-3])
	### FILE EXTENSION FILTER
	if str(fileName[(flen-4):]) == '.txt':# 4 chars in ".txt"
		fileName = fileName[:flen-4]#print("extension removed:" + fileName)
	print("new fileName: ./" + fileName )
	return fileName

#------------------------------------------------------------------
# Legacy function, not favorouable for excel / houdini, or
# general csv reading
#------------------------------------------------------------------        
def writeCSVDict(fileName, tuples, total):
	print("writing csv...")	
	#if file exits already, open and append vaues to correct keys
	#add total count
	ext = ".csv"

	#strip path and txt extension
	fileName = stripPath(fileName)
	
	fil = str(fileName) + ext
	fileName += ext
	#print len(tuples)
	mysum = 0
	with io.open('{0}'.format(fileName),'a', encoding ='utf-8') as f:
		for (k,v) in tuples.iteritems(): #
			#normalise values over total ords parsed
			fv = float(v)/(float(total)) * 100 #percent
			mysum += v
			# word -> actual number -> normalised percentage
			f.write(unicode(str(k) + "\t" + str(v) + "\t" + str(fv) + "\n"))

		#stats
		f.write(unicode("\ntotal specified keywords found:\t" + str(mysum)))	
		f.write(unicode("\ntotal words parsed:\t\t\t" + str(total) + "\n"))
	f.close()
	print("* WroteFile :" + fil)

#------------------------------------------------------------------
#	main CSV output functionality 
#------------------------------------------------------------------        
def writeCSVDictColWise(outfile, tuples, total): #write columnwise
	#print('function -> writeCSVDictColWise')
	#print("writing columnWise csv to: " + outfile + "...")	
	#if file exits already, open and append vaues to correct keys
	ext = ".csv"
	#strip path and txt extension
	fileName = stripPath(outfile)
	fil = str(fileName) + ext
	fileName += ext
	#print len(tuples)
	tsum = 0

	f = io.open('{0}'.format(fileName),'a', encoding ='utf-8')
	#wite col names if first line
	data = ''
	#if file is empty - add the headers
	fsize = os.stat(fileName).st_size
	if fsize == 0:
		print('wiritng header...')
		header = ''
		for k in tuples:
			header += (k + ',' + '\t\t')
		
		print(header)
		f.write(unicode(header) + '\n')
	
	#write data
	for (k,v) in tuples.iteritems(): #
		fv = float(tuples[k])/(float(total)) * 10000 #percent
		fv = decimal.Decimal(fv)
		strfv = str(round(fv,4))# round the decimal
		#print strfv
		data += (strfv + '\t\t')
	data += '\n'
	f.write(unicode(str(data)))
	f.close()
	
	#stats
	#f.write(unicode("\ntotal specified keywords found:\t" + str(tsum)))	
	#f.write(unicode("\ntotal words parsed:\t\t\t" + str(total) + "\n"))

	print(data)
	print("*Wrote to File :" + fil)
#------------------------------------------------------------------    
# timing of search, clean and output
start = time.time()
#------------------------------------------------------------------    
#Process args
sent = args.sent
path = args.path
#------------------------------------------------------------------    
#POSTIVE SENTIMENT FOR IPHONE
if sent == "pos":
	print("sent is pos\n")
	keywords = {#dictionary
		"sleek":0,#handles explosion. exploded, exploding,explodes,explosive
		"beaut":0,#handles beautiful
		"sexy":0,
		"cool":0,
		"awesome":0,
		"love":0, #like can be misconstrued
		"great":0
	}

#NEGATIVE SENTIMENT FOR IPHONE
elif sent == "neg":
	print("sent is neg\n")
	#initialise dict
	keywords = {#dictionary
	"bad":0,
	"ugly":0,
	"hissing":0, #covers smokign, smokey, smoke
	"recall":0,# could be a neutral word
	"shelve":0,
	"fail":0
}

search_results = []
size = 25 # number of results to return
total = 0
v = 1 #optional version identifier suffix for fileName

#path = "../output/leg/aug/samsung/"
#path no longer hardcoded, but taken from Cmd Line args
#ie use python multiMine1.py --path /my/New/Path/

files = [f for f in listdir(path) if (isfile(join(path, f)) and (str(f[(len(f)-4):]) == ".txt"))]
#and (str(f[(len(f)-4):]) == ".txt"))]

#sort by file num
sortedFiles = list(files)
#check
print "files has " + str(len(sortedFiles)) + " items"

for fileName in files:

	end = len(fileName)-4
	start = len(fileName)-6
	fileNum = int(fileName[start:end])
	print "fileNum: " + str(fileNum)

	sortedFiles[fileNum-1] = fileName
	print ("added " + fileName + " to list sortedFiles in index: " + str(fileNum-1))

for fileName in sortedFiles:
	extension = str(fileName[(len(fileName)-4):])
	if extension != ".txt":
		print ('incorrect fiie extension...')
	else:
		print("processing " + fileName + "...")
		
		#f = unicode(f,errors='ignore')
		f = path + '/' + fileName
		tweetFile = open(str(f),'r').read().decode('utf-8')
		search_results = word_tokenize(tweetFile)
		total += len(search_results)
		if total == 0:#avoid divide by zero error
			total = total + 1
		# additive process
		keywords = analyse_content(search_results, keywords, size)
		#Rowwise write individual files
		outfile = f
		#print outfile		
		#writeCSVDict(outfile, keywords, total) #file gets the query name, and total words parsed data
		writeCSVDictColWise(('iphone_' + sent), keywords, total) #write columnwise
#------------------------------------------------------------------        
# timing - Ideally collect into an array of times and print at the end 
# of a multi query
end = time.time()
exec_time = end - start
exec_time /= 1000

#------------------------------------------------------------------        
print('\nelapsedTime(sec): ' + str(int(exec_time)))
print
#end
