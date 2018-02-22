from bs4 import BeautifulSoup as bs
import datascience as ds
import sys
import os
import re

SCRAPING_DIRECTORY = "./scraped_files/"
DATABASE_DIRECTORY = "./database_files/"

TABLE_FILE_NAME = "beige_books.csv"

START_FLAGS = ["Summary of Commentary", "National Summary"]
ENG_FLAGS = ["Return to top", "Back to Top"]
BREAK_FLAGS = ["For more information about "]

TOPIC_LENGTH = 50

# TODO: Find generalizable structure in all documents
# TODO: Get parser to work
# TODO: Add detailed commentary


def main():
    raw_files = os.listdir(SCRAPING_DIRECTORY)  # Lists all the files that were scraped
    final_table = new_table()
    parsing_flags = flag_array()
    for w in raw_files:  # Reads and prints the 'text content' of all the scraped files
        site = load(w)
        parse(site, final_table, parsing_flags)
    save(final_table)


def new_table():
    new = ds.Table()
    new = new.with_column("ID", []).with_column("Data", []).with_column("District Number", [])
    new = new.with_column("Sector Heading", []).with_column("Sector Text", [])
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
    file.close()
    website = bs(file_contents, 'html.parser')
    return website


def parse(site, table, flags):
    text = site.find_all(text=True)
    for t in text:
        filtered_text = re.sub('\s+', ' ', t).strip().replace("\n", " ")
        if filtered_text == "":
            continue
        elif contains(filtered_text, START_FLAGS):
            print("This is a start flag.")
            err_print(filtered_text)
        elif contains(filtered_text, ENG_FLAGS):
            print("This is an end flag.")
            err_print(filtered_text)
        elif contains(filtered_text, BREAK_FLAGS):
            print("This is a break flag.")
            err_print(filtered_text)
        else:
            print("There are no flags connected.")
            err_print(filtered_text)
    return


def contains(str, str_arr):
    for s in str_arr:
        if str in s:
            return True
    return False


def save(table):
    if os.path.isfile(TABLE_FILE_NAME):
        os.remove("beige_books.csv")
    table.to_csv("beige_books.csv")


def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":  # Because this is good practice apparently
    main()
