from bs4 import BeautifulSoup as bs
import datascience as ds
import os

SCRAPING_DIRECTORY = "./scraped_files/"
DATABASE_DIRECTORY = "./database_files/"


def main():
    raw_files = os.listdir(SCRAPING_DIRECTORY)  # Lists all the files that were scraped

    for w in raw_files:  # Reads and prints the 'text content' of all the scraped files
        file = open(SCRAPING_DIRECTORY + w, 'r')
        file_contents = ""
        for line in file:
            file_contents += line
        website = bs(file_contents, 'html.parser')
        print(website.get_text())


def new_table():
    new = ds.Table()
    new = new.with_column("ID", [])
    new = new.with_column("Data", [])
    new = new.with_column("District Number", [])
    new = new.with_column("Sector Heading", [])
    new = new.with_column("Sector Text", [])
    return new


def parse(report_html, table):
    headings = site.find_all("p")
    for heading in headings:
        print(heading)
    return table


def

if __name__ == "__main__":  # Because this is good practice apparently
    main()
