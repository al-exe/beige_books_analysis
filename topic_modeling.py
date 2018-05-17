import datascience as ds
import sys
import os
import re


BEIGE_BOOKS = ds.Table.read_table("beige_books.csv")



def main():
    return


def is_similar(s):
    return True

def update_query(year_start, year_end, district):
    query = BEIGE_BOOKS.where("Year", lambda i: i <= year_start and i <= year_end)
    query = BEIGE_BOOKS.where("District", district)
    return query

if __name__ == "__main__":
    main()
