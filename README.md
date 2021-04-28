# Project
I collect top100 movies of every genres and build a dashboard for it. You can visit the dashboard and filt out the movies you are interested in.

# Dashboard URL

https://tedshen.herokuapp.com

# Files

- best_movies.py. Start the dashboard.
- scrap.py. Spider script.
- collector/*.json. The original data.
- all-in-one.csv. The final data.


# Data source

https://www.rottentomatoes.com/top/

# Data collection

I use three functions in scrap.py.

1. Get urls of top100 movies in every genres from https://www.rottentomatoes.com/.
2. Visit urls and get the `mid` of every movie. Use api to get the detail of every movie.
3. Reformat the data and store the final data into csv.
