#------------------------------------------------------------------
# This code thankfully acknowledges the python from the book
# "Mining the Social Web " (2nd Edition) by M. Russel
# and the tutorials by Harrison on the youtube channel "sentdex"
# this code developed by daniel phillis
# SID 2110633, FAN phil0411
# with the help mentioned above
#------------------------------------------------------------------

# this code (all) developed by daniel phillis
# SID 2110633, FAN phil0411
# with the help mentioned above

# this file is dependent on the existence of 
# 3 list pickles - docs, words, word_features
# and 7 classifer pickles
# all_words.pickle
'''
all_words.pickle
docs.pickle
word_features.pickle

lrc.pickle
lsvc.pickle
mnnbc.pickle
nbc.pickle
bnbc.pickle
nusvc.pickle
sgdc.pickle
'''
# they sould probably be available in the same path as the python script

#------------------------------------------------------------------
# sentiment analysis module
#------------------------------------------------------------
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import opinion_lexicon
from nltk.corpus import words
from nltk.classify.scikitlearn import SklearnClassifier

import random
import time
import pickle

#scikit learn is more of an artificial learning machine toolkit
# these classification algorithms weree used but not deeply researched
# wikipedia has some intersting articles on them but be prepared for some 
# heavy math (2nd and third year or beyond)

from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from statistics import mode

#---------------------------------------------------------------------------
# A custom classifier class to simply tally the results
# of the real algorithmic classifiers
#---------------------------------------------------------------------------
class VoteClassifier(ClassifierI) :
        def __init__(self, *classifiers):
                #we will pass as arguments a list of classifiers tot his class for voting
                self._classifiers = classifiers

        def classify(self, features):
                votes = []
                for c in self._classifiers:
                        v = c.classify(features)# get the vote from each classifier 
                        votes.append(v)
                return mode(votes) #who go the most votes
        # recall mode is the value that appears most often in a set of data

        def confidence(self, features):
                votes = []
                for c in self._classifiers:
                        v = c.classify(features)
                        votes.append(v)
                        
                choice_votes = votes.count(mode(votes))
				# counts how many occurances of the most  popular votes
                confidence =  choice_votes / len(votes) #confidence of that vote, 
				#a certainty
                return confidence

                choice_votes = votes.count(mode(votes))
                
#-------------------------------------------------------------------------------
# movie reviews that is 'pickled' (I think of it as compiled) to docs.pickle
# these files represent the training text - the text that the algorithm 'learns' from
# the information provided by these files is basically a set of human-written
# movie reviews and whether or not they have overall pos or neg sentiment

##short_pos = open('../short_reviews/positive_enc.txt','r').read().decode('utf-8')
##short_neg = open('../short_reviews/negative_enc.txt','r').read().decode('utf-8')

# NB these external dependencies above are repaced in this scrtipt by pickle (similar to compiled)
# files
 
##docs = []
##all_words = []
#j = adjective, r = adverb, v = verb

'''
allowedTypes = ["J"]

for p in short_pos.split('\n'):
	docs.append( (p, "pos") )
	words = word_tokenize(p)
	pos = nltk.pos_tag(words)
	for w in pos:
		if w[1][0] in allowedTypes:
			all_words.append(w[0].lower())	

for p in short_neg.split('\n'):
	docs.append( (p, "neg") )
	words = word_tokenize(p)
	# this nltk.pos is not changed to neg,its not short for positive
	neg = nltk.pos_tag(words)
	for w in neg:
		if w[1][0] in allowedTypes:
			all_words.append(w[0].lower())	

'''
# the loading of pickle files here (similar to compiled objects)
# replaces the code commented out above
# the pickle loading can likewise be commented out and the original code restored
# however with out pickling any code the performance is severly degraded - taking 
# approx 5 to 10 mins to print results of the classification algorithms
# due to the amount of text to parse

#----load-docs-pickle------------
docs_f = open("pickle_files/docs.pickle","rb")
docs = pickle.load(docs_f)
docs_f.close()

# all_words = nltk.FreqDist(all_words) # we need the order provided by a FreqDist
# we wont focus on the values# (ie the words not the freq associated with it)

#------load the word_features_pickle-----------
all_words_f = open('pickle_files/all_words.pickle','rb')
all_words = pickle.load(all_words_f)
all_words_f.close()

#word_features = list(all_words.keys()[:3000])#for the top 5000 words only
#------load the word_features_pickle-----------
word_features_f = open('pickle_files/word_features.pickle','rb')
word_features = pickle.load(word_features_f)
word_features_f.close()

#---------------------------------------------------------------------------

def find_features(document):
        words = word_tokenize(document)
        features = {} #defines a dictionary
        for w in word_features: #the top 5000 words from all words
                features[w] = (w in words)# this creates the boolean value

        return features   # returns a dict with keys but not values     

#---------------------------------------------------------------------------
featureSets = [(find_features(rev), category) for (rev,category) in docs]
random.shuffle(featureSets) #shuffle must be done to avoid bias

#These two sets must be different to avoid bias
trainingSet = featureSets[:5000] #before 10000
testingSet = featureSets[5000:] # after 10000
#---------------------------------------------------------------------------
#classifier = nltk.NaiveBayesClassifier.train(trainingSet)
#---------------------------------------------------------------------------

#CLASSIFIERS

#------load the vanilla NBCpickle-----------
nbc_f = open('pickle_files/nbc.pickle','rb')
classifier = pickle.load(nbc_f)
nbc_f.close()

#print("Vanilla Naive Bayes Algo accuracy%: ", 
#      nltk.classify.accuracy(classifier, testingSet)*100)

#tell us the most popular words on both sides (pos and neg)
#classifier.show_most_informative_features(15)
#---------------------------------------------------------------------------

#MultinomialNB_classifier = SklearnClassifier( MultinomialNB() )
#MultinomialNB_classifier.train(trainingSet)

#------load the MN-NBC pickle-----------
mnbc_f = open('pickle_files/mnnbc.pickle','rb')
MultinomialNB_classifier = pickle.load(mnbc_f)
mnbc_f.close()

#print("MultinomialNaiveBayes Algo accuracy%: ", 
#      nltk.classify.accuracy(MultinomialNB_classifier, testingSet)*100)

#BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
#BernoulliNB_classifier.train(trainingSet)

#------load the B-NBC pickle-----------
bnbc_f = open('pickle_files/bnbc.pickle','rb')
BernoulliNB_classifier = pickle.load(bnbc_f)
bnbc_f.close()

#print("BernoulliNaiveBayes Algo accuracy%: ", 
#      nltk.classify.accuracy(BernoulliNB_classifier, testingSet)*100)

#LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
#LogisticRegression_classifier.train(trainingSet)

#------load the LRC pickle-----------
lrc_f = open('pickle_files/lrc.pickle','rb')
LogisticRegression_classifier = pickle.load(lrc_f)
lrc_f.close()

#print("LogisticRegression Algo accuracy%: ", 
#      nltk.classify.accuracy(LogisticRegression_classifier, testingSet)*100)

#SGDClassifier_classifier = SklearnClassifier(SGDClassifier())
#SGDClassifier_classifier.train(trainingSet)

#------load the SGDC pickle-----------
sgdc_f = open('pickle_files/sgdc.pickle','rb')
SGDClassifier_classifier = pickle.load(sgdc_f)
sgdc_f.close()

#print("StochGradientClassifier Algo accuracy%: ", 
#      nltk.classify.accuracy(SGDClassifier_classifier, testingSet)*100)

#LinearSVC_classifier = SklearnClassifier(LinearSVC())
#LinearSVC_classifier.train(trainingSet)


#------load the LSVC pickle-----------
lsvc_f = open('pickle_files/lsvc.pickle','rb')
LinearSVC_classifier = pickle.load(lsvc_f)
lsvc_f.close()

#print("LinearSVC Algo accuracy%: ", 
#      nltk.classify.accuracy(LinearSVC_classifier, testingSet)*100)

#NuSVC_classifier = SklearnClassifier(NuSVC())
#NuSVC_classifier.train(trainingSet)

#------load the nuSVC pickle-----------
nusvc_f = open('pickle_files/nusvc.pickle','rb')
NuSVC_classifier = pickle.load(nusvc_f)
nusvc_f.close()

#print("NuSVC Algo accuracy%: ", 
#      nltk.classify.accuracy(NuSVC_classifier, testingSet)*100)

#---------------------------------------------------------------------------
# vote on all the classifier results

voted_classifier = VoteClassifier(
	classifier, #the regular classifier
    MultinomialNB_classifier,
    BernoulliNB_classifier,
    LogisticRegression_classifier,
    SGDClassifier_classifier,# stochastic gradient descent
    LinearSVC_classifier,
    NuSVC_classifier
)
#---------------------------------------------------------------------------
# print results of all the classification algorithms

print ("Mutinomial NB Classification:", voted_classifier.classify(testingSet[1][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[1][0])*100)

print ("Bernoulli Classification:", voted_classifier.classify(testingSet[2][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[2][0])*100)

print ("Logistic Regression Classification:", voted_classifier.classify(testingSet[3][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[3][0])*100)

print ("Stoch gradient Descent Classification:", voted_classifier.classify(testingSet[4][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[4][0])*100)

print ("Linear Vector Classification:", voted_classifier.classify(testingSet[5][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[5][0])*100)

print ("Nu SVector Classification:", voted_classifier.classify(testingSet[6][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[6][0])*100)

print ("Classification:", voted_classifier.classify(testingSet[0][0]),
       "Confidence%:", voted_classifier.confidence(testingSet[0][0])*100)

print("Voted Classifier Accuracy %: ",
      nltk.classify.accuracy(voted_classifier, testingSet)*100)

#---------------------------------------------------------------------------

def sentiment(text):
	feats = find_features(text)#get the word_features (top x000 words)
	# from that text
	return voted_classifier.classify(feats), voted_classifier.confidence(feats)*100
