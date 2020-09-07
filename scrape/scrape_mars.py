from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time

import sys
sys.path.append("..")
from config import chromedriver_path

def scrape(exe_path = chromedriver_path):
    """
    Scrapes information from multiple websites
    to get information on Mars.

    Parameters
    ----------
    exe_path : str, optional
            The executable path for a browser driver, by default is the chromedriver_path in config.py

    Returns
    -------
    [dict]
        Contains information on Mars.
    """
    scraper = Mars_Scraper(exe_path)
    return scraper.scrape_all_data()

class Mars_Scraper:
    """
    This class contains code to scrape information about Mars.
    """
    def __init__(self, exe_path = chromedriver_path):
        """
        Initializes the Mars_Scraper class and opens a new browser session.

        Parameters
        ----------
        exe_path : str, optional
            The executable path for a browser driver, by default is the chromedriver_path in config.py
        """
        self.exe_path = exe_path
        self.init_chrome_browser()

    def __del__(self):
        """
        On deconstruction, will close the browser if not already closed.
        """
        if(self.browser is not None):
            self.close_browser()
    
    def init_chrome_browser(self):
        """
        Opens a Chrome Browser using splinter.
        """
        executable_path = {"executable_path": self.exe_path}
        self.browser = Browser("chrome", **executable_path, headless = False)

    def close_browser(self):
        """
        Closes the browser.
        """
        self.browser.quit()
    
    def get_soup(self, url):
        """
        Gets the HTML from a URL as a BeatifulSoup object.

        Parameters
        ----------
        url : [str]
            The url to get the html from.

        Returns
        -------
         [BeatifulSoup]
            This object contains the HTML.
        """
        browser = self.browser
        browser.visit(url)
        time.sleep(.2) # Make sure the page is loaded before moving on.
        html = browser.html
        soup = BeautifulSoup(html)
        return soup
    
    def get_latest_nasa_news(self):
        """
        Gets the latest nasa news article information.

        Returns
        -------
        [dict]
            Dictionary containing "title" and "paragraph" keys.
        """
        browser = self.browser

        nasa_news_url = "https://mars.nasa.gov/news/"
        nasa_soup = self.get_soup(nasa_news_url)

        latest_news_soup = nasa_soup.find("div", class_="list_text")

        latest_title_soup = latest_news_soup.find("div", class_="content_title")
        latest_title = latest_title_soup.get_text()

        latest_paragraph_soup = latest_news_soup.find("div", class_="article_teaser_body")
        latest_paragraph = latest_paragraph_soup.get_text()

        nasa_news_latest = {
            "title" : latest_title,
            "paragraph" : latest_paragraph
        }

        return nasa_news_latest

    def get_mars_space_featured_image(self):
        """
        Gets the featured image from NASA JPL.

        Returns
        -------
        [dict]
            Dictionary containing "img_url" and "title" nodes.
        """
        browser = self.browser

        jpl_base_url = "https://www.jpl.nasa.gov"
        jpl_url = f"{jpl_base_url}/spaceimages/?search=&category=Mars"
        jpl_soup = self.get_soup(jpl_url)

        jpl_header_soup = jpl_soup.find("article")
        partial_url = jpl_header_soup.find("a").get("data-fancybox-href")
        featured_image_url = f"{jpl_base_url}{partial_url}"

        return {
            "img_url" : featured_image_url,
            "title" : "Featured Mars Image"
        }

    def get_mars_facts_table_df(self):
        """
        Gets the planet profile facts for Mars.

        Returns
        -------
        [DataFrame]
            The table containing Mars facts.
        """
        mars_facts_url = "https://space-facts.com/mars/"
        mars_facts_tables = pd.read_html(mars_facts_url)
        mars_planet_profile = mars_facts_tables[0]
        return mars_planet_profile

    def get_mars_facts_table_html(self):
        """
        Gets the planet profile facts for Mars in an HTML format.

        Returns
        -------
        [str]
            Contains the html for displaying Mars facts.
        """
        mars_planet_profile = self.get_mars_facts_table_df()

        mars_planet_profile_html = mars_planet_profile.to_html(index=False, header=False)

        return mars_planet_profile_html

    def get_mars_hemisphere_images(self):
        """
        Gets hemisphere images of Mars

        Returns
        -------
        [list of dict]
            Dictionaries containing "title" and "img_url" keys.
        """
        browser = self.browser

        hemisphere_root = "https://astrogeology.usgs.gov"
        hemisphere_url = f"{hemisphere_root}/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        hemisphere_soup = self.get_soup(hemisphere_url)

        hemisphere_list_soup = hemisphere_soup.find("div", class_="results")

        hemisphere_image_urls = []
        items = hemisphere_list_soup.find_all("div", class_="item")
        for item_soup in items:
            item_link = item_soup.find("a").get("href")
            image_page_soup = self.get_soup(f"{hemisphere_root}{item_link}")
            image_title = image_page_soup.find("h2").get_text()
            image_download_soup = image_page_soup.find_all("div", class_="downloads")[0]
            image_url = image_download_soup.find("a").get("href")
            hemisphere_image_url = {
                "title" : image_title,
                "img_url" : image_url
            }
            hemisphere_image_urls.append(hemisphere_image_url)
        
        return hemisphere_image_urls

    def scrape_all_data(self):
        """
        Runs through multiple website to get information on Mars.

        Returns
        -------
        [dict]
            Contains information on Mars.
        """
        nasa_news = self.get_latest_nasa_news()
        featured_image = self.get_mars_space_featured_image()
        mars_facts_html = self.get_mars_facts_table_html()
        hemi_images = self.get_mars_hemisphere_images()

        return {
            "nasa_news" : nasa_news,
            "featured_image" : featured_image,
            "mars_facts_html" : mars_facts_html,
            "hemisphere_images" : hemi_images
        }
