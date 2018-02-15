from bs4 import BeautifulSoup as bs
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

if __name__ == "__main__":  # Because this is good practice apparently
    main()
