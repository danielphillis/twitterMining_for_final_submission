#------------------------------------------------------------------
# This code thankfully acknowledges the python from the book
# "Mining the Social Web " (2nd Edition) by M. Russel
# and the tutorials by Harrison on the youtube channel "sentdex"
# this code developed by daniel phillis
# SID 2110633, FAN phil0411
# with the help mentioned above
#------------------------------------------------------------------

################################################################################
# summary
# 
# Warning
# written on ubuntuMate v1.12.1 with python 2.7.12
# probably wont work on Python version 3.x

# script is looped over multiple quieries (from a hardcoded predefined list)
# override queries to run on only one query - see comments below
# ie queries = "#Hillary" vs ["query_one","query_two", "etc"]

# Only one csv file is now written for all queries as pposed to one per query

# exisitng csv files are appened to if the same script is run more than once
# resulting in duplicate row titles (each queries results are on a row)

# function for cleaning data called from with in analyse function
# so as to maintian the correct data structures required by the functions
# ideally would filter all but adjectives for sentiment analysis

# Analyse function pulls all text from the tweet

# csv written contains a *nowmalised* (new) frequency analysis of keywords
# - (the predefined list) the tally is divided by the total amoutn of words parsed

# time in seconds is printed
# resulting csv filesize printin is omitted
################################################################################
import sys
import subprocess
from subprocess import call
import time
import datetime
import twitter
import io
import csv
import nltk
from nltk.corpus import stopwords
from prettytable import PrettyTable
from collections import Counter

#------------------------------------------------------------------
# do login dance
def oauthlogin():
  CONSUMER_KEY = 'SIeOam4mLD8sZWr7QHmE67zHi'
  CONSUMER_SECRET = '444wPQutVPhns6ff8gdiWCrifgxkw4A6itsiPl3EQw5MhcQRDc'
  OAUTH_TOKEN = '29954818-FRyNn2iHYP9QsK1srs2SQTWdxRPBygkm1mb6Fda2x'
  OAUTH_TOKEN_SECRET = 'RUk8dVC5QJaXK9um6ADZvPSuGlzRiOSpusYs8SACRN6Yq'

  auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
  CONSUMER_KEY, CONSUMER_SECRET)
  twitter_api = twitter.Twitter(auth=auth)
  return twitter_api
#------------------------------------------------------------------

def twitter_search(twitter_api, q,count, max_results, **kw):
  #See https://dev.twitter.com/docs/api/1.1/get/search/tweets

  print ("adding twitter search results from query \'" + q + "\'")

  search_results = twitter_api.search.tweets(q=q, count=count, **kw)
  statuses = search_results['statuses']
  max_results = min(1000, max_results) #enforce a reasonable limit to searches
  #max_results = 100 # number of tweets texts to be combines into a search
  #remember multiple searches are being done here	
  for _ in range(max_results):#10 * 100 = 1000
    try:
    	next_results = search_results['search_metadata']['next_results']
    except KeyError, e: # No more results when next_results doesn't exist
    	break
    #key word arguments, create a dictionary from next results
    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])
    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']
    if len(statuses) > max_results:
      break
  return statuses

#------------------------------------------------------------------

def analyse_content(data, keywords, size, entityThreshold=3):

	#Optimisation
	if len(data) == 0:
		print("No data to analyze")
		return
	#Compute a collection of all words from all tweets
	status_texts = [ status['text'] for status in data ]
	words = [ w
		for t in status_texts
			for w in t.split()]#was 'for w in t.split() if w[0] != '#']'
			#for w in t.split() if w not in stopwords.words("english")]

	words = clean(words)
	size = 25
	c = Counter(words).most_common(size)

	# Compute frequencies *with a dictionary (tuples)
	tups = [ (k,v) for (k,v) in c if v >= entityThreshold ]

	#pt is suitable for console display but not for writing a csv to disk
	pt = PrettyTable(field_names=['Entity', 'Count'])	
	[ pt.add_row(kv) for kv in tups ]
	pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment
	#print pt

	# for each item in the keywords dict, count the re-occurances ie a 
	# Freq Dist for a specific subset
	for w in words:
		for k in keywords:
			if ('' + k) in ('' + w):
				keywords[k] = keywords[k] + 1 #increase the value of key k
	#print "keywords"
	#print keywords #prints each word to a new line	

	return keywords#an array of tuples
#------------------------------------------------------------------        
# clean(items)
# clean accepts type list, outputs type list
# clean detects adjectives using NLTK Natural Language tool kit
# (www.nltk.org) to help narrow down sentiment
# clean removes nltk.stopwords
# clean converts all elements in the input list to lowercase 
# clean ignores hashtags (#example) when building output list
# clean ignores twitter usernames (@username) when building output list
# clean also gives a before and after count of elements

def clean(items):
	
	#this still has the twitter meta data structure
	before = len(items)

	stop_words = stopwords.words("english")
	#print stop_words
	#exit()

	#custom exclusions
	stop_words += ["RT","rt","the","he","He","of","in","is",
					"his","His","a","&amp"]
		
	for item in items:
		low = item.lower()
		items.remove(item)
		
		#j = adjective, r = adverb, v = verb
		allowedTypes = ["J"]
		#if low in stop_words:
		#	items.remove(low)
		
		if low not in stop_words:
			pos = nltk.pos_tag([low])#pos = part of speech ie JJ for adjective
			#print("pos" +  pos[1][0])
			for w in pos:
				#detect adjectives
				#if w[1][0] in allowedTypes:#and (w[1][0] != '#'): #is w an adjective but not a hashtag
					#print 'adjective detected: ' + w[0]
				items.append(w[0].lower())	#w[0] is thw word as opposed to the POS 
	cleaned = []

	#remove hashtags and twitter usernames from reuslts
	for i in items:
		if (i[0] != '#') or (i[0] !='@'):#gfilter out hashtags and twitter usernames
			cleaned.append(i)

	after = before - len(cleaned)
	print ('words scrubbed away:' + str(after))
	#print cleaned
	return cleaned
#------------------------------------------------------------------    
# f is file handle
# fil is file name for printing

def writeCSVDict(filename, tuples, total):
	#if file exits already, open and append vaues to correct keys
	#add total count
	ext = ".csv"
	fil = str(filename) + ext
	filename += ext
	#print len(tuples)
	mysum = 0

	with io.open('{0}'.format(filename),'a', encoding ='utf-8') as f:
		for (k,v) in tuples.iteritems(): #
			mysum += v#tally the values
			#normalise the values over all words parsed
			
			# could also normalise over all matches wich would 
			#tell us proportions of matches compared to each other
			fv = float(v)/float(total)
			f.write(unicode(str(k) + "\t\t" + str(fv) + "\n") )
		f.write(unicode("total specified keywords found:\t" + str(mysum) + "\n"))
		f.write(unicode("total words parsed:\t" + str(total) + "\n"))
	f.close()
	print("wrote file :" + fil)

#------------------------------------------------------------------    
# write to csv (all filtration should be done by now)
# tweet per line gives us an easy way to count lines

def writeCSVData(filename,data):
	ext = ".csv"
	fil = str(filename) + ext
	filename += ext
	ats = 0
	tweets = 0
	with io.open('{0}'.format(filename),'a', encoding ='utf-8') as f:
		f.write(unicode('\n<tweet>')) #to count tweet searches tweets will be 10 x this ?
		tweets +=10
		for i in data:
			#tweets = tweets + 1
			if i[0] == '@':
				#print("\n")
				#f.write(unicode('\n\n')) 	#ensure_ascii=0 no longer works?  # 0 was false but didnt work
				ats = ats+1 				#count '@' symbols
				#f.write(unicode('\t\n')) 		#we dont want a new line for ever word
											#as this makes it harder to discern individual tweets
			f.write(unicode(i + " "))#spacing !!!
		
	f.close()
	print "#-#-------------------------------------"
	print(str(ats) + ' @\'s found')
	print(str(tweets) + ' tweets harvested') #not accurate ?
	print("wrote file :" + fil)
#------------------------------------------------------------------       

# timing of search, clean and output
start = time.time()

#usage
queries = ["#samsung","#Samsung",
			"#SamsungGalaxyNote7", 
			"#Note7",
			#"#GalaxyNote7Edge",
			"#Note7Edge",
			"#GalaxyNote7"
			]

#EXAMPLE QUERIES

#queries = ["#apple", "#Apple", "#iPhone7", "#iPhone"]
#queries += ["#iWatch"]
#queries = ["Note7", "SamsungGalaxyNote7", "Galaxy Note7"]
#queries = ["iWatch"]
#queries = ["trump"]


keywords_neg = {#dictionary
	"explo":0,
	"fire":0,
	"smok":0,
	"recall":0,
	"stop":0,
	"shelved":0,
	"disastor":0,
	"fail":0
}

keywords_pos = {#dictionary
	"cool":0,
	"happy":0,
	"love":0,
	"xoxo":0,
	"awesome":0,
	"cant wait":0,
	"nice":0,
	"the best":0
}

#search_keys = [keywords_neg, keywords_pos]

count = 100
twitter_api = oauthlogin()
search_results = []
v = 1 #optional version identifier suffix for filename
total = 0
#Cutomise output path
#path = "../output/csv_tues/"
path = ''
name = ''
#q = q + path


for q in queries:
	name += ('_' + q)
	
	#v =  v+1 #version	#handy to group files by version
	search_results += twitter_search(twitter_api, q, count, max_results=100)
	total = len(search_results)

	size = 25
	# additive process
	keywords = analyse_content(search_results, keywords_neg, size) #prints a prettyTable
	#returns a dictionary?/array of tuples for writing a FREQ DIST	
	
name = (name + path + "_" + str(v))# append output path and version number to query text

#MERGED RESULTS
#ONLY wirte the one fule with all query results merged
writeCSVDict(name, keywords, total) #file gets the query name

#------------------------------------------------------------------        
# timing - Ideally collect into an array of times and print at the end 
# of a multi query
end = time.time()
exec_time = end - start
#------------------------------------------------------------------        
print ('elapsedTime(sec): ' + str(int(exec_time)))
#endcd
