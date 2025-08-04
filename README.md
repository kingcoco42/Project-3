This is Team 69's Project 3 for COP3530 Data Structures and Algorithms at the University of Florida.

# Project Proposal
## Problem Statement
Our group aims to create an interface that allows for fast lookup of the k-sized set of players most similar to a given NBA player for a variety of skill groups, such as scoring and defense.

## Motivation
NBA teams with a starting five loaded with stars are frequently defeated because of a lack of chemistry or depth. The ability to accurately identify archetypal groups of players could allow teams to fill in their weaknesses and maximize team synergy by acquiring players that fit a specific, necessary role. This capacity could be particularly useful in identifying under-the-radar players whose overall impact may be low but who excel at a particular facet of the game (e.g. a low-scoring defensive specialist) or provide a complementary role to a team’s existing players. 

## Solution?
The problem is “solved” when we are able to enter any NBA player within the dataset and efficiently return their “neighborhood” of similar players for the selected group of characteristics (e.g. scoring profile). 

## Data sets
Five datasets (traditional, advanced, scoring, defense, impact)
- Link to Repository Containing All Datasets: https://github.com/Brescou/NBA-dataset-stats-player-team/tree/main/player
- Uncleaned Combined Dataset: https://docs.google.com/spreadsheets/d/1qnwJTQ5nmBNe4_pMH0n8FRRoVlDwhsvoyNMip2DkZFo/edit?usp=sharing

## Tools
Python(numpy, matplotlib, pandas, Flask, Flask-CORS, scikit-learn), C++, JavaScript

## Strategy
Strategy: Exact k-Nearest Neighbors using a KD tree and Approximate Nearest Neighbors to compile similar players, both using vectors.

## Roles
- John Ziska - Approximate Nearest Neighbors Algorithm
- Luke Phommachanh - K-Nearest Neighbors Algorithm
- Victer Qiu - UI

## References
- K-Nearest Neighbors: https://www.geeksforgeeks.org/machine-learning/k-nearest-neighbours/
- Approximate Nearest Neighbors: https://www.geeksforgeeks.org/machine-learning/approximate-nearest-neighbor-ann-search/
- KD Trees: https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/KDtree.html

# Instructions
## Frontend React and Vite
Change directories into where you want your project
`cd path/to/where/you/want/you./project`
Then run `npx create-vite`
- When prompted, type `y` to continue
- Choose `React` for `framework` and select `JavaScript` for `variant`
- Enter a project name for both `Project name` and `Package name`

Change directories to your new file `cd your-project-name` and install dependencies `npm install`

Now copy over this repo's UI files into your `src` file.

Now you are ready to run it, `npm run dev` it will provide a link to http://localhost:5173/ where you can see the frontend.

## Backend Flask and Python
Create and activate virtual environment
`cd path/to/backend/folder`
`python -m venv venv`
`.\venv\Scripts\Activate.ps1`

Once the virtual environment is activated, copy over the files under this repo's algorithms into your folder.
then run `python -m pip install --upgrade pip` and `python -m pip install -r requirements.txt`

Lastly, run the flask_app.py, `python flask_app.py`, all the backend stuff with happen at http://localhost:8080/api
Good luck building your best NBA team.
