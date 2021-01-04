# DO NOT MODIFY CLASS NAME
import pickle


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # {term : [NumOfDiffDocs, {tweetID : inverted_docs[tweetID]}, NumOfCurrInTweetInCorpus]}
        self.inverted_docs = {}  # {tweetID : {term : [max_tf, repAmount, numOfUniqueWords, doc_length]}}
        self.config = config
        self.EntityDict = {}
        self.number_of_documents = 0


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        self.number_of_documents += 1
        document_dictionary = document.term_doc_dictionary
        self.BuildingDict(document.tweet_id, document_dictionary, document.doc_length)

    #TODO : change 'postingDict' -> 'inverted_idx'
    def BuildingDict(self, tweetID, document_dictionary, doc_length):
        max_tf, num_unique_terms = self.calc_tf_unique(document_dictionary, 0, 0)  # entitydict is empty
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                if term.isalpha():

                    """can get into inverted index - This part is for the Entity Dict inserting"""

                    if ' ' in term and len(self.EntityDict) >= 0 and term not in self.EntityDict:  # first time
                        self.EntityDict[term] = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                        continue
                    elif ' ' in term and len(self.EntityDict) > 0 and type(self.EntityDict[term]) == dict:
                        dict_from_new = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                        dict_to_add = {**(self.EntityDict[term]), **dict_from_new}
                        self.EntityDict[term] = 2
                        self.inverted_idx[term] = [2, dict_to_add]
                        continue
                    elif ' ' in term and self.EntityDict[term] == 2:
                        self.inverted_idx[term][0] += 1
                        continue

                    """get inside inverted index properly"""

                    lowterm = term.lower()  # max
                    upterm = term.upper()  # MAX
                    # Case 1
                    if term.islower():
                        if upterm in self.inverted_idx:  # M -- we will keep m and drop M (add recurrences to m)
                            dict_from_lower = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                            dict_to_add = {**(self.inverted_idx[upterm][1]), **(dict_from_lower)}
                            self.inverted_idx[term] = [1 + self.inverted_idx[upterm][0], dict_to_add]
                            self.inverted_idx.pop(upterm)
                        else:
                            self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)
                    # Case 2
                    elif term.isupper():
                        if lowterm in self.inverted_idx:  # m -- we will keep m and drop M (add recurrences to m)
                            self.inverted_idx[lowterm][0] += 1
                            self.inverted_idx[lowterm][1][tweetID] = [max_tf, document_dictionary[term],num_unique_terms, doc_length]
                        else:
                            self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)

                else:
                    """if term isn't a word, but hashtag, crucit or number"""
                    self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,num_unique_terms, doc_length)
            except:
                print('problem with the following key {}'.format(term[0]))

    def adding_term_if_not_on_inverted(self, term, repAmount, tweetID, max_tf, numOfUniqueWords, doc_length):
        self.inverted_idx[term] = [1, {tweetID: [max_tf, repAmount, numOfUniqueWords, doc_length]}]

    # calculate values for each document
    def calc_tf_unique(self, document_dictionary, num_unique_terms, max_tf):
        for term in document_dictionary.keys():
            # can get into inverted index
            num_unique_terms += 1
            if max_tf < document_dictionary[term]:
                max_tf = document_dictionary[term]
        return max_tf, num_unique_terms


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        with open(fn, "rb") as file:
            return pickle.load(file), file

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        # in the pickle file we wil save the inverted_idx and inverted_docs in list
        pickle_save = []  # [inverted_idx, inverted_docs]
        # sort before save
        self.inverted_idx = dict(sorted(self.inverted_idx.items(), key=lambda e: e[1][0]))
        self.inverted_docs = dict(sorted(self.postingDict.items(), key=lambda e: e[1][0]))
        pickle_save[0] = self.inverted_idx
        pickle_save[1] = self.inverted_docs
        with open(fn, 'wb') as file:
            pickle.dump(pickle_save, file)
        file.close()

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term, inverted_idx):
        """
        Checks if a term exist in the dictionary.
        """
        return term in inverted_idx

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, terms):
        """
        Return the posting list from the index for a term.
        """
        inverted_idx = self.load_index(self.config.get_savedFileInverted())[0]
        terms_posting = {}
        for term in terms:
            if not self._is_term_exist(term.lower(), inverted_idx) and not self._is_term_exist(term.upper(), inverted_idx):
                continue
            if self._is_term_exist(term.lower(), inverted_idx):
                term_to_save = term.lower()
            elif self._is_term_exist(term.upper(), inverted_idx):
                term_to_save = term.upper()
            if self._is_term_exist(term_to_save):
                terms_posting[term_to_save] = inverted_idx[term_to_save]
        return terms_posting

    def get_doc_posting_list(self, terms):
        """
        Return the posting list from the index for a doc.
        """


    def get_inverted_docs(self):
        inverted_docs = self.load_index(self.config.get_savedFileInverted())[1]
        return inverted_docs

    def get_number_of_documents(self):
        return self.number_of_documents


