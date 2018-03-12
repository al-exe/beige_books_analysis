import gensim
import logging

def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    sentences = [['first', 'sentence'], ['second', 'sentence']]
    model = gensim.models.Word2Vec(sentences, min_count=1)

if __name__ == "__main__":
    main()