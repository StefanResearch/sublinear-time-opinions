#!/bin/zsh

for OPINIONTYPE in 1 2 4
do
	for DATASET in Advogato GooglePlus Flickr Flixster Pokec TwitterFollows YouTube LiveJournal
	do
		julia Main.jl $DATASET $OPINIONTYPE
	done
done
