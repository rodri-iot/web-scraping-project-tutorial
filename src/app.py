# Web scraping

#In this project, we are going to obtain and analyze data about Tesla's profit, which we will previously store in a DataFrame and in a sqlite database.

## Step 1: Install dependencies

#Make sure you have the Python `pandas` and `requests` packages installed to be able to work on the project. In case you do not have the libraries installed, run them in the console:

#bash
#pip install pandas requests


## Step 2: Download HTML

#The download of the HTML of the web page will be done with the `requests` library, as we saw in the module theory.

#The web page we want to scrape is the following: [https://ycharts.com/companies/TSLA/revenues](https://ycharts.com/companies/TSLA/revenues). It collects and stores information about the growth of the company every three months, since June 2009. It stores the text scraped from the web in some variable.

# Imports
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd


# Select the resource to download
url = "https://ycharts.com/companies/TSLA/revenues"
# Modify request headers to make it appear that the request is coming from a legitimate browser
headers = {
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
}

# Request to download the file from the internet
response = requests.get(url, headers=headers)
response
# If the request has been executed correcly (code 200), then the HTML content of the page has been downloaded

## Step 3: Transform the HTML

#The next step to start extracting the information is to transform it into a structured object. Do this using `BeautifulSoup`. Once you have interpreted the HTML correctly, parse it to:

#1. Find all the tables.
#2. Find the table with the quarterly evolution.
#3. Store the data in a DataFrame.

if response:
    # We transform the flat HTML into real HTML
    soup = BeautifulSoup(response.text, 'html')
    soup

# Show content by response
response.content

# Find the table with the quarterly evolution
table = soup.find("table")
rows = table.find_all("tr")
data = []

for row in rows:
    cells = row.find_all(["td", "th"])
    cells = [cell.get_text(strip = True) for cell in cells]
    data.append(cells)
data

## Step 4: Process the DataFrame

#Next, clean up the rows to get clean values by removing `$` and commas. Remove also those that are empty or have no information.

df = pd.DataFrame(data)

# Extract row[0]
my_columns = df.loc[0, :].to_list()
df.columns = my_columns

# Show less row [0]
df = df[1:]
df

# Create a new DF clean
clean_df = df.copy()
clean_df

clean_df.info()

# Clean column per column
clean_df['Date'] = pd.to_datetime(clean_df['Date'])
clean_df['Value'] = clean_df['Value'].str.replace("B", "")
clean_df.info()

# Show Data Frame Clean
clean_df

## Step 5: Store the data in sqlite

#Create an empty instance of the database and include the clean data in it, as we saw in the database module. Once you have an empty database:

#1. Create the table.
#2. Insert the values.
#3. Store (`commit`) the changes.

import os
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
from dotenv import load_dotenv
import sqlite3
# load the .env file variables
load_dotenv()

con = sqlite3.connect("tesla_revenue.db")

# Create the table
con.execute("""CREATE TABLE IF NOT EXISTS tesla_revenue (Date DATE, Value REAL)""")
con.commit()

# con.executemany("""INSERT INTO tesla_revenue(Date, Value) VALUES (?, ?)""", clean_df)

clean_df.to_sql("tesla_revenue", con, if_exists="append", index=False)
con.commit()

# Show
for row in con.execute("""SELECT * FROM tesla_revenue"""):
    print(row)

clean_df.info()

## Step 6: Visualize the data

#What types of visualizations can we make? Suggest at least 3 and plot them.

import matplotlib.pyplot as plt
import seaborn as sns

# Fig 1
fig, axis = plt.subplots(figsize = (10, 5))

clean_df['Value'] = clean_df['Value'].astype('float')
sns.lineplot(data= clean_df, x= 'Date', y= 'Value')

plt.tight_layout()
plt.show()

# Fig 2
fig, axis = plt.subplots(figsize = (10, 5))

clean_df["Date"] = pd.to_datetime(clean_df["Date"])
tesla_revenue_yearly = clean_df.groupby(clean_df["Date"].dt.year)["Value"].sum().reset_index()
sns.barplot(data = tesla_revenue_yearly[tesla_revenue_yearly["Date"] < 2023], x= "Date", y= "Value")

plt.tight_layout()

plt.show()

# Fig 3
fig, axis = plt.subplots(figsize = (10, 5))

clean_df["Date"] = pd.to_datetime(clean_df["Date"])
tesla_revenue_monthly = clean_df.groupby(clean_df["Date"].dt.month)["Value"].sum().reset_index()
sns.barplot(data = tesla_revenue_monthly, x= "Date", y= "Value")

plt.tight_layout()

plt.show()