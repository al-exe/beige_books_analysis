import gensim as gs
import logging
import os

SCRAPING_DIRECTORY = ""

PRINT_STATUS = True

def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    sentences = [['first', 'sentence'], ['second', 'sentence']]
    model = gs.models.Word2Vec(sentences, min_count=1)


def clean():
    print("Fix me!")


def err_print(*args, status=PRINT_STATUS, **kwargs):
    """ Helper function for easy prints to std err """
    if status:
        try:
            print(*args, file=sys.stderr, **kwargs)
        except UnicodeEncodeError:
            print("Invalid unicode character", file=sys.stderr)

if __name__ == "__main__":
    main()
