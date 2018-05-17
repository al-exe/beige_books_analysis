import scraper
import parser
import cleaner
import randomize_batches
import word2vec


def main():
    scraper.main()
    parser.main()
    cleaner.main()
    word2vec.main()
    randomize_batches.main()


if __name__ == "__main__":
    main()
