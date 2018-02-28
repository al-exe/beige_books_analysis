from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import shutil
import sys
import os

ARCHIVE_URL = "https://www.minneapolisfed.org/news-and-events/beige-book-archive"
WEBDRIVER_PATH = "./webdriver/chromedriver.exe"

SEARCH_BUTTON_XPATH = '//*[@id="bb_search"]/input'
SELECT_ID = "bb_year"
HTML_LINK_XPATH = "//a[@href]"

URL_IDENTIFIER = "https://www.minneapolisfed.org/news-and-events/beige-book-archive/"
CURRENT_YEAR = 2018
MAX_YEAR = CURRENT_YEAR + 1

SCRAPING_DIRECTORY = "./scraped_files/"

# TODO: Add comprehensive comments
# TODO: Clean up repetitive or messy code
# TODO: Create scrapers for the multiple books and/or merge them with this scraper


def main():
    err_print("Booting up web driver...")
    beige_books = webdriver.Chrome(WEBDRIVER_PATH)
    err_print("Loading main archive page...")
    beige_books.get(ARCHIVE_URL)
    err_print("Loading XPATH and ID identifiers...")
    search_button = beige_books.find_element_by_xpath(SEARCH_BUTTON_XPATH)
    selects = Select(beige_books.find_element_by_name(SELECT_ID)).options
    err_print("Selecting all possible years...\n")
    reports = []
    curr_year = CURRENT_YEAR
    while curr_year >= 1970:
        year = selects[index_from_year(curr_year)]
        err_print("Grabbing all reports for " + str(curr_year) + "...")
        year.click()
        search_button.click()
        links = beige_books.find_elements_by_xpath(HTML_LINK_XPATH)
        for link in links:
            link_html = link.get_attribute("href")
            if contains(URL_IDENTIFIER + str(curr_year), link_html) and link_html not in reports:
                err_print("Grabbed " + link_html + "!")
                reports.append(link_html)
        err_print("Finished " + str(curr_year) + "!")
        curr_year -= 1
        err_print("Refreshing parameters for " + str(curr_year) + "...\n")
        search_button = beige_books.find_element_by_xpath(SEARCH_BUTTON_XPATH)
        selects = Select(beige_books.find_element_by_name(SELECT_ID)).options
    err_print("Clearing old files...")
    delete_directory(SCRAPING_DIRECTORY)
    err_print("Saving reports to directory...")
    for report in reports:
        save(report)
    err_print("Scraping complete!")


def soupify(url):
    raw_html = requests.get(url).content
    return bs(raw_html, 'html.parser')


def contains(pre_str, full_str):
    return pre_str in full_str


def index_from_year(year):
    return -year + MAX_YEAR


def save(report_html):
    contents = soupify(report_html).prettify()
    name = report_html[-10:]
    err_print("Saving " + report_html + " as " + name + ".html...")
    new_file = open(SCRAPING_DIRECTORY + name + '.html', 'w', encoding="utf-8")
    new_file.write(contents)
    new_file.close()


def delete_directory(directory):
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        os.makedirs(directory)


def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()
