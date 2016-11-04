#!/bin/bash
$count_tweets = 0
for i in $( ls Aug_*.txt ); do
	#!echo $i
	#!len = grep '@' $i | wc -l
 	grep '@' $i | wc -l
	#!echo $len
	#!$count_tweets = $count_tweets + $len
done
#!echo 'total tweets'
#!echo $count_tweets

