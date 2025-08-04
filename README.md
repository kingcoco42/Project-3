This is Team 69's Project 3 for COP3530 Data Structures and Algorithms at the University of Florida.

# Project Proposal
## Problem Statement
Our group aims to create an interface that allows for fast lookup of the k-sized set of players most similar to a given NBA player for a variety of skill groups, such as scoring and defense.

## Motivation
NBA teams with a starting five loaded with stars are frequently defeated because of a lack of chemistry or depth. The ability to accurately identify archetypal groups of players could allow teams to fill in their weaknesses and maximize team synergy by acquiring players that fit a specific, necessary role. This capacity could be particularly useful in identifying under-the-radar players whose overall impact may be low but who excel at a particular facet of the game (e.g. a low-scoring defensive specialist) or provide a complementary role to a team’s existing players. 

## Solution?
The problem is “solved” when we are able to enter any NBA player within the dataset and efficiently return their “neighborhood” of similar players for the selected group of characteristics (e.g. scoring profile). 

## Data sets
Data: Four datasets (traditional, advanced, scoring, defense)
Link to Repository Containing All Datasets: https://github.com/Brescou/NBA-dataset-stats-player-team/tree/main/player
Uncleaned Combined Dataset: https://docs.google.com/spreadsheets/d/1qnwJTQ5nmBNe4_pMH0n8FRRoVlDwhsvoyNMip2DkZFo/edit?usp=sharing

## Tools
Python(numpy, matplotlib, pandas, Flask, Flask-CORS, scikit-learn), C++, JavaScript

## Strategy
Strategy: Exact k-Nearest Neighbors using a KD tree and Approximate Nearest Neighbors to compile similar players, both using vectors.

## Roles
John Ziska - Approximate Nearest Neighbors Algorithm
Luke Phommachanh - K-Nearest Neighbors Algorithm
Victer Qiu - UI

## References
K-Nearest Neighbors: https://www.geeksforgeeks.org/machine-learning/k-nearest-neighbours/
Approximate Nearest Neighbors: https://www.geeksforgeeks.org/machine-learning/approximate-nearest-neighbor-ann-search/
KD Trees: https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/KDtree.html

# Instructions
