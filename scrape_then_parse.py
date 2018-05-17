from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datascience as ds
import requests
import re
import sys
import os

ARCHIVE_URL = "https://www.minneapolisfed.org/news-and-events/beige-book-archive"
WEBDRIVER_PATH = "./webdriver/chromedriver.exe"

SEARCH_BUTTON_XPATH = '//*[@id="bb_search"]/input'  # For easy access to XPATH
SELECT_ID = "bb_year"  # For easy access to the select ID
HTML_LINK_XPATH = "//a[@href]"  # For easy access to html XPATH

URL_IDENTIFIER = "https://www.minneapolisfed.org/news-and-events/beige-book-archive/"
CURRENT_YEAR = 2018  # Current year of scraping
MAX_YEAR = CURRENT_YEAR + 1
END_YEAR = 1970  # First year of archive

SCRAPING_DIRECTORY = "./scraped_files/"  # Save all htmls to here
TABLE_FILE_NAME = "beige_books.csv"

START_FLAGS = ["Beige Book Report: ", "Beige Book: "]  # List of flags to start parsing data
END_FLAGS = ["Latest Content from the Minneapolis Fed", "For more information about "]  # List of flags to stop parse

MAX_TOPIC_LENGTH = 50  # To delimit between text and topic
GLOBAL_ID = 1  # Counter for section IDs

# The following gives us easy conversion from string month to numerical month
DATE_DICTIONARY = {"January": '1', "February": '2', "March": '3', "April": '4', "May": '5', "June": '6', "July": '7'}
DATE_DICTIONARY.update({"August": '8', "September": '9', "October": '10', "November": '11', "December": '12'})


def main():
    """ Main call for all scraping. Returns nothing and no errors (should) be thrown. """
    err_print("Booting up web driver...")
    beige_books = webdriver.Chrome(WEBDRIVER_PATH)  # Webdriver loaded from folder in case PATH not configured
    err_print("Loading main archive page...")
    beige_books.get(ARCHIVE_URL)
    err_print("Loading XPATH and ID identifiers...")
    search_button = beige_books.find_element_by_xpath(SEARCH_BUTTON_XPATH)  # Easy button pressing
    selects = Select(beige_books.find_element_by_name(SELECT_ID)).options  # Grab all available options
    err_print("Selecting all possible years...\n")
    reports = []
    curr_year = CURRENT_YEAR

    while curr_year >= END_YEAR:  # While loop used becuase 'selects' change on every iteration and useful for indexing
        year = selects[index_from_year(curr_year)]  # Loads the year into memory
        err_print("Grabbing all reports for " + str(curr_year) + "...")
        year.click()
        search_button.click()
        links = beige_books.find_elements_by_xpath(HTML_LINK_XPATH)  # Grabs all hyperlinks

        for link in links:
            link_html = link.get_attribute("href")  # Converts Selenium object to string URLs
            if contains(URL_IDENTIFIER + str(curr_year), link_html) and link_html not in reports:  # Checks for dupes
                err_print("Grabbed " + link_html + "!")
                reports.append(link_html)

        err_print("Finished " + str(curr_year) + "!")
        curr_year -= 1  # Since the current year is the first item on the select, deincrement after every loop
        err_print("Refreshing parameters for " + str(curr_year) + "...\n")
        search_button = beige_books.find_element_by_xpath(SEARCH_BUTTON_XPATH)  # Refresh needed because site changed
        selects = Select(beige_books.find_element_by_name(SELECT_ID)).options

    err_print("Closing web driver...")
    beige_books.close()  # Exits out of the website
    err_print("End of scrape!")

    # START OF PARSING #

    err_print("Instantiating new data table...")
    final_table = new_table()  # Creates a new table to store data
    err_print("Parsing reports to table...\n")
    for report in reports:  # Reads the 'text content' of all the scraped files and parses them into the final table
        err_print("Extracting data from " + report + "...")
        site = soupify(report)
        final_table = parse(site, final_table)
    save(final_table)  # Saves the table into a CSV
    err_print("End of parse!")


def parse(site, table):
    """
    Where all of the magic / parsing happens. Takes a website and extracts all relevant
    information from the website and stores said information into a table.

    :param site: 'Soupified' website
    :param table: Final output table that stores all data
    :return: The inputted table but mutated to include new data
    """
    global GLOBAL_ID  # Loads the unique IDs from Global frame to current frame

    # Instantiates empty fields for data of interest
    Date = ""
    District = ""
    Heading = ""
    Text = ""

    # Instantiates parsing flags for easy parsing control flow
    text_flag = False
    date_start = False
    first_topic = False
    pre_date = ""

    text = site.find_all(text=True)  # Extracts all non-html text from the website
    for t in text:
        # The following formats all text to remove extraneous whitespace
        filtered_text = re.sub('\s+', ' ', t).strip().replace("\n", " ")
        if filtered_text == "":  # Skip empty strings
            continue
        elif contains_flag(filtered_text, START_FLAGS) and not text_flag:  # Start flag for data retrieval!
            District = filtered_text.split(":")[1].strip()
            date_start = True  # Next line should be the date
            if District == "National Summary":  # Ignore National Summaries for now until we fix all bugs
                err_print("Ignoring Nation Summaries for now.")
                date_start = False
        elif date_start:  # Extracts the date from the website
            if pre_date == "":
                try:
                    Date = numeric_date(filtered_text)
                    date_start = False
                    text_flag = True  # Next lines should be the textual data
                    first_topic = True  # Next line should be the first topic
                except KeyError:
                    pre_date = filtered_text
            else:  # Special Edge case for Minneapolis November 1st, 1995
                Date = numeric_date(pre_date + filtered_text)
                date_start = False
                text_flag = True
                first_topic = True
                pre_date = ""
        elif text_flag:
            if contains_flag(filtered_text, END_FLAGS):  # End flag for data retrieval
                table = add_data(table, [str(GLOBAL_ID), Date, District, Heading, Text])  # Save final blobs
                GLOBAL_ID += 1  # Increment Global ID by one for next website pass through
                break
            elif len(filtered_text) > MAX_TOPIC_LENGTH and first_topic:
                Heading = "Summary of Economic Activity"  # Lack of topic means following text is a summary
                Text += filtered_text
                first_topic = False
            elif len(filtered_text) < MAX_TOPIC_LENGTH and first_topic:
                Heading = filtered_text  # Continue as normal
                first_topic = False
            elif len(filtered_text) < MAX_TOPIC_LENGTH and not first_topic:
                table = add_data(table, [str(GLOBAL_ID), Date, District, Heading, Text])  # Conclusion of a topic
                Text = ""
                Heading = filtered_text
                GLOBAL_ID += 1
            elif len(filtered_text) > MAX_TOPIC_LENGTH and not first_topic:  # Multi-paragraph text handling
                Text += filtered_text
    return table


def soupify(url):
    """ Helper function to convert a string URL to a bs4 object """
    raw_html = requests.get(url).content
    return bs(raw_html, 'html.parser')


def contains(pre_str, full_str):
    """ Using a function looks nicer than using the below code """
    return pre_str in full_str


def index_from_year(year):
    """ Converts a year to the specified index in the select """
    return -year + MAX_YEAR


def new_table():
    """
    Creates an empty table with the following columns: ID to enumerate all possible
    heading - text pairs, Date to store the date of every beige book published, District
    to store the name of the district, Sector Heading to give the associated text a
    broad topic description, and Sector Text to contain the actual text of interest.
    """
    new = ds.Table()
    new = new.with_column("ID", []).with_column("Date", []).with_column("District", [])
    new = new.with_column("Sector Heading", []).with_column("Sector Text", [])
    return new


def contains_flag(string, str_arr):
    """ Helper function to check is a certain string is a flag """
    for s in str_arr:
        if s in string:
            return True
    return False


def numeric_date(date_str):
    """ Helper function to convert string date to numeric date """
    final_date = ""
    date = date_str.split(" ")
    final_date += DATE_DICTIONARY[date[0]] + "-"
    final_date += date[1][:-1] + "-"
    final_date += date[2]
    return final_date


def add_data(table, row):
    """ Helper function to add data to table """
    err_print("ID: " + row[0])
    err_print("Date: " + row[1])
    err_print("District: " + row[2])
    err_print("Heading: " + row[3])
    err_print("Text: " + row[4])
    table = table.with_row(row)
    return table


def save(table):
    """
    Saves new table into a .csv file with all data collected for future use.
    """
    if os.path.isfile(TABLE_FILE_NAME):
        os.remove("beige_books.csv")
    table.to_csv("beige_books.csv")


def err_print(*args, **kwargs):
    """ Helper function for easy prints to std err """
    try:
        print(*args, file=sys.stderr, **kwargs)
    except UnicodeEncodeError:
        print("Invalid unicode character", file=sys.stderr)

if __name__ == "__main__":  # Because this is good practice apparently
    main()
