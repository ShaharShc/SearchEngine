# DO NOT MODIFY CLASS NAME
import pickle


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # {term : NumOfDiffDocs, NumOfCurrInTweetInCorpus}
        self.postingDict = {}  # {term : NumOfDiffDocs,{tweetID:[[max_tf, repAmount, numOfUniqueWords, doc_length]}
        self.config = config
        self.EntityDict = {}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        self.BuildingDict(document.tweet_id, document_dictionary, document.doc_length)

    def BuildingDict(self, tweetID, document_dictionary, doc_length):
        max_tf, num_unique_terms = self.calc_tf_unique(document_dictionary, 0, 0)  # entitydict is empty
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                if term.isalpha():
                    # can get into inverted index and the to posting
                    if ' ' in term and len(self.EntityDict) >= 0 and term not in self.EntityDict:  # first time
                        self.EntityDict[term] = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                        continue
                    elif ' ' in term and len(self.EntityDict) > 0 and type(self.EntityDict[term]) == dict:
                        dict_from_new = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                        dict_to_add = {**(self.EntityDict[term]), **dict_from_new}
                        self.EntityDict[term] = 2
                        self.postingDict[term] = [2, dict_to_add]
                        # occurInCorpus = document_dictionary[term] + sum(self.EntityDict[term].values()[1])
                        self.inverted_idx[term] = [2, document_dictionary[term]]
                        continue
                    elif ' ' in term and self.EntityDict[term] == 2:
                        # changed
                        self.inverted_idx[term][0] += 1
                        # changed
                        self.inverted_idx[term][1] += document_dictionary[term]
                        self.postingDict[term][0] += 1
                        continue
                    lowterm = term.lower()  # max
                    upterm = term.upper()  # MAX
                    # Case 1
                    if term.islower():
                        if upterm in self.inverted_idx:  # M -- we will keep m and drop M (add recurrences to m)
                            if upterm in self.postingDict:
                                dict_from_lower = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                                dict_to_add = {**(self.postingDict[upterm][1]), **(dict_from_lower)}
                                self.postingDict[term] = [1 + self.postingDict[upterm][0], dict_to_add]
                                # EDITING INV INDEX'S TERM NUM OF DIFF TWEETS
                                data_to_copy = self.inverted_idx.pop(upterm)
                                # changed
                                data_to_copy[0] += 1
                                self.inverted_idx[term] = data_to_copy
                                # changed
                                self.inverted_idx[term][1] += document_dictionary[term]
                                self.postingDict.pop(upterm)
                            else:
                                # EDITING INV INDEX'S TERM NUM OF DIFF TWEETS
                                data_to_copy = self.inverted_idx.pop(upterm)
                                # changed
                                data_to_copy[0] += 1
                                self.inverted_idx[term] = data_to_copy
                                # changed
                                self.inverted_idx[term][1] += document_dictionary[term]
                                self.postingDict[term] = [1, {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}]
                        else:
                            self.adding_term_if_not_on_posting(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)
                    # Case 2
                    elif term.isupper():
                        if lowterm in self.inverted_idx:  # m -- we will keep m and drop M (add recurrences to m)
                            if lowterm in self.postingDict:
                                self.postingDict[lowterm][0] += 1
                                self.postingDict[lowterm][1][tweetID] = [max_tf, document_dictionary[term],
                                                                         num_unique_terms, doc_length]
                                # EDITING INV INDEX'S TERM NUM OF DIFF TWEETS
                                # changed
                                self.inverted_idx[lowterm][0] += 1
                                # changed
                                self.inverted_idx[lowterm][1] += document_dictionary[term]
                            else:  # We already emptied post_dict with the lowterm - so we'll create new to new
                                # post_dict
                                self.postingDict[lowterm] = [1, {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}]
                                # changed
                                self.inverted_idx[lowterm][0] += 1
                                # changed
                                self.inverted_idx[lowterm][1] += document_dictionary[term]
                        else:
                            self.adding_term_if_not_on_posting(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)
                # if term isn't a word, but hashtag, crucit or number
                else:
                    self.adding_term_if_not_on_posting(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)
            except:
                print('problem with the following key {}'.format(term[0]))

    def removeDict(self):
        self.postingDict.clear()

    def adding_term_if_not_on_posting(self, term, repAmount, tweetID, max_tf, numOfUniqueWords, doc_length):

        if term not in self.postingDict and term in self.inverted_idx:  # term is in posting file that we've emptied
            self.postingDict[term] = [1, {tweetID: [max_tf, repAmount, numOfUniqueWords, doc_length]}]
            # changed
            self.inverted_idx[term][0] += 1
            # changed
            self.inverted_idx[term][1] += repAmount
        else:
            self.term_to_posting_and_inverted(term, repAmount, tweetID, max_tf, numOfUniqueWords, doc_length)

    # calc values for each document
    def calc_tf_unique(self, document_dictionary, num_unique_terms, max_tf):
        for term in document_dictionary.keys():
            # can get into inverted index
            num_unique_terms += 1
            if max_tf < document_dictionary[term]:
                max_tf = document_dictionary[term]
        return max_tf, num_unique_terms


    def term_to_posting_and_inverted(self, term, repAmount, tweetID, max_tf, numOfUniqueWords, doc_length):
        # changed to adjust to PartC
        dict_of_this_tweet = {tweetID: [max_tf, repAmount, numOfUniqueWords, doc_length]}
        if term not in self.inverted_idx:
            self.inverted_idx[term] = [1,repAmount]
            self.postingDict[term] = [1, dict_of_this_tweet]
        else:  # update posting and inverted
            self.postingDict[term][0] += 1
            self.postingDict[term][1] = {**dict_of_this_tweet, **self.postingDict[term][1]}
            # changed
            self.inverted_idx[term][0] += 1
            # changed
            self.inverted_idx[term][1] += repAmount

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        # raise NotImplementedError

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        # raise NotImplementedError
        # SORT BEFORE GETTING IN
        self.inverted_idx = dict(sorted(self.inverted_idx.items(), key=lambda e: e[1][0]))
        self.postingDict = dict(sorted(self.postingDict.items(), key=lambda e: e[1][0]))
        # with open(filename, 'wb') as file:
        #     pickle.dump(self.inverted_idx, file)
        # file.close()





    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []
