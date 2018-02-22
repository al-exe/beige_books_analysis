from bs4 import BeautifulSoup as bs
import datascience as ds
import os
import re

SCRAPING_DIRECTORY = "./scraped_files/"
DATABASE_DIRECTORY = "./database_files/"

START_FLAG = ""
ENG_FLAGS = ["Return to top", "Back to Top"]
BREAK_FLAGS = ["For more information about "]

# TODO: Find generalizable structure in all documents
# TODO: Get parser to work


def main():
    raw_files = os.listdir(SCRAPING_DIRECTORY)  # Lists all the files that were scraped
    final_table = new_table()
    parsing_flags = flag_array()
    for w in raw_files:  # Reads and prints the 'text content' of all the scraped files
        site = load(w)
        parse(site, final_table)
    save(final_table)


def new_table():
    new = ds.Table()
    new = new.with_column("ID", [])
    new = new.with_column("Data", [])
    new = new.with_column("District Number", [])
    new = new.with_column("Sector Heading", [])
    new = new.with_column("Sector Text", [])
    return new


def flag_array(type=0):
    flags1 = []
    flags2 = []
    flags3 = []
    flags1.extend(["First District--Boston", "Second District--New York", "Third District--Philadelphia"])
    flags1.extend(["Fourth District--Cleveland", "Fifth District--Richmond", "Sixth District--Atlanta"])
    flags1.extend(["Seventh District--Chicago", "Eighth District--St. Louis", "Ninth District--Minneapolis"])
    flags1.extend(["Tenth District--Kansas City", "Eleventh District--Dallas", "Twelfth District--San Francisco"])
    for f in flags1:
        flags2.append(f.replace("--", " - "))
    for f in flags1:
        flags3.append("Federal Reserve Bank of " + f.split("--")[1])
    flags = flags1 + flags2 + flags3
    return flags


def load(file_name):
    file = open(SCRAPING_DIRECTORY + file_name, 'r', encoding="utf-8")
    file_contents = ""
    for line in file:
        file_contents += line
    website = bs(file_contents, 'html.parser')
    return website


def parse(site, table):
    text = site.find_all(text=True)
    for t in text:
        filtered_text = re.sub('\s+', ' ', t).strip().replace("\n", " ")
        if filtered_text != "":
            print(filtered_text)
    return table


def save(table):
    os.remove("beige_books.csv")
    table.to_csv("beige_books.csv")

if __name__ == "__main__":  # Because this is good practice apparently
    main()
