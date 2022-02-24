# car-scrape
www.carsales.com.au scrape to csv, configurable top 15 picks

Pretty basic car scraper. Inputs are configured in main and are for simply filtered carsales searches. If you require a complex query... 
Construct it on the website and put the URL in the python script in main. 

Script will write a database file based on the fields in main.. it will sort, filter and rank using 3 columns (price, kms, year) to attempt to 
show only the most reasonable cars. Will write a new csv and text file with picks as well as output to console. 

The ranking algorithm is configurable by increasing the priority of any of the 3 details mentioned previously. 
