# UFC Scraper
This project scrapes fight statistics and fighter details from ufcstats.com for all historical UFC events. The `data` folder contains two csv files, `fight_hist.csv` and `fighter_stats.csv`, data for all fights and fighters recent as of 04/13/2024 (UFC Fight 300).

A writeup of an analysis done with this data and Neo4j can be found here: https://towardsdatascience.com/ranking-the-best-ufc-fighters-using-pagerank-and-neo4j-5385805b4515

An updated version of the analysis using new data and Networkx can be found in the `analysis` folder.

All code used in the writeup above is in the `analysis` folder.

## Scripts
Additionally, the `scripts` folder contains a file called `ufc_scraper.py` which has functions used for both the initial scraping and functions used to update the data as new UFC events occur.

### Usage Examples
Usage examples can also be found in the notebook `scrape_fights.ipynb` in the `scripts` folder.

#### Getting UFC Fight and Fighter Details

##### Initial fight stats pull:

`fight_hist = get_all_fight_stats()`

##### Initial fighter details pull:

`fighter_details = get_fighter_details(fight_hist.fighter_url.unique())`

where `fight_hist` is a dataframe of fight statistics and `fighter_url` being a column of urls linking to individual fighter pages.

#### Updating UFC Fight and Fighter Stats

##### Updating fight stats:

`fight_hist_updated = update_fight_stats(fight_hist)`

where `fight_hist` is a dataframe of already saved fight statistics. `fight_hist_updated` will be a dataframe of updated fight stats up to the most recent UFC card.

##### Updating fighter statistics:

`fighter_stats_updated = update_fighter_details(fight_hist_updated.fighter_url.unique(), fighter_stats)`

where `fight_hist_updated` is a dataframe of updated fight stats and `fighter_url` being a column of urls linking to individual fighter pages. `fighter_stats` is a dataframe of already saved fighter details. `fighter_stats_updated` will be an updated dataframe of fighter details for all fighters who have made an appearance in the UFC.
