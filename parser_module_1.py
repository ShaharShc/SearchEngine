import collections
import json
import spacy
import re  # For preprocessing
from gensim.models.phrases import Phrases, Phraser
from nltk import TweetTokenizer
from document import Document

class Parse_1:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")


    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        tweet_tokenizer = TweetTokenizer()
        text_tokens = tweet_tokenizer.tokenize(text)
        text_tokens = [token for token in text_tokens if not token.find("https") != -1]
        text = ' '.join(text_tokens)
        brief_cleaning = self.nlp((re.sub("[^A-Za-z']+", ' ', str(text)).lower()))
        doc = self.cleaning(brief_cleaning)
        tokens = doc.split()

        return tokens

    def cleaning(self, doc):
        txt = [token.lemma_ for token in doc if not token.is_stop]
        # Word2Vec uses context words to learn the vector representation of a target word,
        # if a sentence is only one or two words long,
        # the benefit for the training is very small
        return ' '.join(txt)


    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        if doc_as_list[3] is None or doc_as_list[3] == '{}':
            url = None
        else:
            url = json.loads(doc_as_list[3])
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        if doc_as_list[6] is None or doc_as_list[6] == '{}':
            retweet_url = None
        else:
            retweet_url = json.loads(doc_as_list[6])
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        if doc_as_list[9] is None or doc_as_list[9] == '{}':
            quote_url = None
        else:
            quote_url = json.loads(doc_as_list[9])
        quote_indices = doc_as_list[10]
        retweet_quote_text = doc_as_list[11]
        retweet_quote_indices = doc_as_list[12]

        check_RT = full_text[:2]
        if check_RT == 'RT':
            return None

        tokenized_text = self.parse_sentence(full_text)
        doc_length = len(tokenized_text)  # after text operations.

        #dict of all terms (after stemming if true + entities)
        term_dict = dict(collections.Counter(x for x in tokenized_text if x))

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)

        return document

