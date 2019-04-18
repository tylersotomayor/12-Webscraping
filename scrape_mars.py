import pandas as pd
import requests
import time
from bs4 import BeauitfulSoup
import pymongo
from splinter import Browser

def scrape():
	#Set up splinter browser
	executable_path = {'executable_path':'/usr/local/bin/chromedriver'}
	browser = Browser('chromer', **executable_path, headless = False)
	
	# Visit url
	url = "https://mars.nasa.gov/news/"
	browser.visit(url)

	# Pull html text and parse
	html_code = browser.html
	soup = BeautifulSoup(html_code, "html.parser")

	## NASA Mars News
	# Grab news title and paragraph text
	news_title = soup.find('div', class_ = "bottom_gradient").text
	news_p = soup.find('div', class_="rollover_description_inner").text

	## JPL Mars Space Images - Featured Image¶
	## Featured image url 
	jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
	browser.visit(jpl_url)

	# navigate to link
	browser.click_link_by_partial_text('FULL IMAGE')
	time.sleep(20)
	browser.click_link_by_partial_text('more info')

	# get html code once at page
	image_html = browser.html

	# parse
	soup = BeautifulSoup(image_html, "html.parser")

	# find path and make full path
	image_path = soup.find('figure', class_='lede').a['href']
	featured_image_url = "https://www.jpl.nasa.gov/" + image_path

	##Mars Weather
	marsweather_url = "https://twitter.com/marswxreport?lang=en"
	browser.visit(marsweather_url)

	weather_html = browser.html

	soup = BeautifulSoup(weather_html, 'html.parser')

	mars_weather = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text

	##Mars Facts
	# mars facts url and splinter visit
	facts_url = "https://space-facts.com/mars/"
	browser.visit(facts_url)

	# get html
	facts_html = browser.html

	soup = BeautifulSoup(facts_html, 'html.parser')

	# get the entire table
	table_data = soup.find('table', class_="tablepress tablepress-id-mars")

	#find all instances of table row
	table_all = table_data.find_all('tr')

	# set up lists to hold td elements which alternate between label and value
	labels = []
	values = []

	# for each tr element append the first td element to labels and the second to values
	for tr in table_all:
	    td_elements = tr.find_all('td')
	    labels.append(td_elements[0].text)
	    values.append(td_elements[1].text)
	    
	# make a data frame and view
	mars_facts_df = pd.DataFrame({
	    "Label": labels,
	    "Values": values
	})

	# mars facts dataframe
	mars_facts_df

	# get html code for DataFrame
	fact_table = mars_facts_df.to_html(header = False, index = False)
	fact_table

	## Mars Hemispheres
	# Visit website
	usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
	browser.visit(usgs_url)

	time.sleep(1)

	# Scrape page into Soup
	html = browser.html
	soup = bs(html, "html.parser")

	sources = soup.find_all("a",{"class":"itemLink product-item"})
	links = set(["https://astrogeology.usgs.gov" + link["href"] for link in sources])

	hemisphere_image_urls = []
	for link in links:
	    browser.visit(link)
	    time.sleep(1)
	    
	    html = browser.html
	    soup = bs(html, "html.parser")
	    
	    link_dict = {}
	    img_link = soup.find('img',{"class":"wide-image"})["src"]
	    title = soup.find('h2', {"class":"title"}).text
	    link_dict["title"] = title.split(" Enhanced",1)[0]
	    link_dict["img_link"] = "https://astrogeology.usgs.gov" + img_link
	    
	    hemisphere_image_urls.append(link_dict)
    
    # Store data in a dictionary
	mars_data = {
	    "news_title": news_title,
	    "news_p": news_p,
	    "featured_image_url": featured_image_url,
	    "mars_weather": mars_weather,
	    "html_table": fact_table,
	    "hemisphere_image_urls": hemisphere_image_urls
	}

	# Close the browser after scraping
	browser.quit()
	print(json.dumps(mars_data, indent =4))