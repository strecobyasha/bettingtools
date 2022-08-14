# Bettingtools
Hi everyone. My name is Roman. I'm glad to introduce you a pervert attempt to make a full django website.  
You can see what it looks like in real world: [bettingtools.io](https://bettingtools.io).
It does almost all its stuff on its own, without human help. But actually I can't say it does too many things :)

## What is it?
It's a website, dedicated to football analytics and predictions. It is separated on several blocks.

#### Academy
Predictions are made with machine learning, and this process starts here: academy creates a machine learning model.

#### Scout
Parses data from the API and saves it in the database (yes, you need API key).

#### Camp
Creates all the content: previews, reports, recalculates ratings.

#### Arena
All the data is ready to be shown to the users.

## Installation
If you want to make the same:
1) Complete the .env-file.
2) Execute the command from the root directory:
```bash 
make setup
```
It will deploy the project on your local machine via Docker (you have it, right?)

## Disclaimer
Well, this is absolutely not the best example.

All database connections are made through Django ORM (really, even to save data after API parsing). It's fun, but not the optimum way (SQLAlchemy? Hmm...)

To make predictions with machine learning you need to install tensorflow, which is as heavy as a thousand suns.

I think, that it was something more I wanted to tell you, but it's much more interesting to find out strange things
on your own!

## License
Distributed without any restrictions.
