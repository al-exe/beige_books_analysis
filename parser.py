from bs4 import BeautifulSoup as bs
import datascience as ds
import sys
import os
import re

SCRAPING_DIRECTORY = "./scraped_files/"
TABLE_FILE_NAME = "beige_books.csv"

START_FLAGS = ["Beige Book Report: ", "Beige Book: "]
END_FLAGS = ["Latest Content from the Minneapolis Fed"]
IGNORE_FLAGS = ["For more information about ", "www.", "https://"]

MAX_TOPIC_LENGTH = 50
GLOBAL_ID = 1

DATE_DICTIONARY = {"January": '1', "February": '2', "March": '3', "April": '4', "May": '5', "June": '6', "July": '7'}
DATE_DICTIONARY.update({"August": '8', "September": '9', "October": '10', "November": '11', "December": '12'})

# TODO: Add detailed commentary
# TODO: Refine parser
# TODO: Fix iffy tags with National Summaries


def main():
    raw_files = os.listdir(SCRAPING_DIRECTORY)  # Lists all the files that were scraped
    final_table = new_table()
    for w in raw_files:  # Reads and prints the 'text content' of all the scraped files
        site = load(w)
        final_table = parse(site, final_table)
    save(final_table)


def new_table():
    new = ds.Table()
    new = new.with_column("ID", []).with_column("Date", []).with_column("District Number", [])
    new = new.with_column("Sector Heading", []).with_column("Sector Text", [])
    return new


def load(file_name):
    file = open(SCRAPING_DIRECTORY + file_name, 'r', encoding="utf-8")
    file_contents = ""
    for line in file:
        file_contents += line
    file.close()
    website = bs(file_contents, 'html.parser')
    return website


def parse(site, table):
    global GLOBAL_ID

    Date = ""
    District = ""
    Heading = ""
    Text = ""

    text_flag = False
    date_start = False
    first_topic = False

    text = site.find_all(text=True)
    for t in text:
        filtered_text = re.sub('\s+', ' ', t).strip().replace("\n", " ")
        if filtered_text == "":
            continue
        elif contains(filtered_text, START_FLAGS) and not text_flag:
            District = filtered_text.split(":")[1].strip()
            date_start = True
        elif date_start:
            Date = numeric_date(filtered_text)
            date_start = False
            text_flag = True
            first_topic = True
        elif text_flag:
            if contains(filtered_text, END_FLAGS):
                table = add_data(table, [str(GLOBAL_ID), Date, District, Heading, Text])
                GLOBAL_ID += 1
                break
            elif contains(filtered_text, IGNORE_FLAGS):
                continue
            elif len(filtered_text) > MAX_TOPIC_LENGTH and first_topic:
                Heading = "Summary of Economic Activity"
                Text += filtered_text
                first_topic = False
            elif len(filtered_text) < MAX_TOPIC_LENGTH and first_topic:
                Heading = filtered_text
                first_topic = False
            elif len(filtered_text) < MAX_TOPIC_LENGTH and not first_topic:
                table = add_data(table, [str(GLOBAL_ID), Date, District, Heading, Text])
                Text = ""
                Heading = filtered_text
                GLOBAL_ID += 1
            elif len(filtered_text) > MAX_TOPIC_LENGTH and not first_topic:
                Text += filtered_text
    return table


def contains(string, str_arr):
    for s in str_arr:
        if s in string:
            return True
    return False


def numeric_date(date_str):
    final_date = ""
    date = date_str.split(" ")
    final_date += DATE_DICTIONARY[date[0]] + "-"
    final_date += date[1][:-1] + "-"
    final_date += date[2]
    return final_date


def add_data(table, row):
    print("ID: " + row[0])
    print("Date: " + row[1])
    print("District: " + row[2])
    print("Heading: " + row[3])
    print("Text: " + row[4])
    table = table.with_row(row)
    return table


def save(table):
    if os.path.isfile(TABLE_FILE_NAME):
        os.remove("beige_books.csv")
    table.to_csv("beige_books.csv")


def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":  # Because this is good practice apparently
    main()
