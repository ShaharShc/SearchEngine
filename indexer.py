# DO NOT MODIFY CLASS NAME
import pickle

import utils


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # {term : [NumOfDiffDocs, {tweetID : [max_tf, repAmount, numOfUniqueWords, doc_length]}, NumOfCurrInTweetInCorpus,Cij, globalmethod_term,Sij]}
        self.inverted_docs = {}  # {tweetID : {term : [inverted_idx[term][tweetID], NumOfDiffDocs]}}
        self.config = config
        self.EntityDict = {}
        self.AssocMatrixDetails = {}  # (w1,w2) = Cij
        self.number_of_documents = 0
        self.is_using_global_method = False

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

    # TODO : change 'postingDict' -> 'inverted_idx'
    def BuildingDict(self, tweetID, document_dictionary, doc_length):
        max_tf, num_unique_terms = self.calc_tf_unique(document_dictionary, 0, 0)  # entitydict is empty
        # Go over each term in the doc
        for term in document_dictionary:
            try:
                """can get into inverted index - This part is for the Entity Dict inserting"""
                if ' ' in term and len(self.EntityDict) >= 0 and term not in self.EntityDict:  # first time
                    self.EntityDict[term] = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                    continue
                elif ' ' in term and len(self.EntityDict) > 0 and type(self.EntityDict[term]) == dict:
                    dict_from_new = {tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                    dict_to_add = {**(self.EntityDict[term]), **dict_from_new}
                    # for numOfCurrInCorpus
                    for key, val in self.EntityDict[term].items():
                        LastTweetAmount = val[1]
                        break
                    occurInCorpus = document_dictionary[term] + LastTweetAmount
                    self.EntityDict[term] = 2
                    self.inverted_idx[term] = [2, dict_to_add, occurInCorpus, 0, '', 0]
                    continue
                elif ' ' in term and self.EntityDict[term] == 2:
                    # update inv-index
                    self.inverted_idx[term][0] += 1
                    self.inverted_idx[term][1][tweetID] = [max_tf, document_dictionary[term], num_unique_terms,
                                                           doc_length]
                    self.inverted_idx[term][2] += document_dictionary[term]
                    continue

                if term.isalpha():

                    """get inside inverted index properly"""

                    lowterm = term.lower()  # max
                    upterm = term.upper()  # MAX
                    # Case 1
                    if term.islower():
                        if upterm in self.inverted_idx:  # M -- we will keep m and drop M (add recurrences to m)
                            dict_from_lower = {
                                tweetID: [max_tf, document_dictionary[term], num_unique_terms, doc_length]}
                            dict_to_add = {**(self.inverted_idx[upterm][1]), **(dict_from_lower)}
                            self.inverted_idx[term] = [self.inverted_idx[upterm][0] + 1, dict_to_add,self.inverted_idx[upterm][2] + document_dictionary[term],self.inverted_idx[upterm][3] , '',0]
                            self.inverted_idx.pop(upterm)

                        else:
                            if term in self.inverted_idx:
                                self.inverted_idx[term][0] += 1
                                self.inverted_idx[term][1][tweetID] = [max_tf, document_dictionary[term],
                                                                       num_unique_terms, doc_length]
                                self.inverted_idx[term][2] += document_dictionary[term]

                            else:  # if lower comes more than once
                                self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,
                                                                    num_unique_terms, doc_length)

                    # Case 2
                    elif term.isupper():
                        if lowterm in self.inverted_idx:  # m -- we will keep m and drop M (add recurrences to m)
                            self.inverted_idx[lowterm][0] += 1
                            self.inverted_idx[lowterm][1][tweetID] = [max_tf, document_dictionary[term],
                                                                      num_unique_terms, doc_length]
                            self.inverted_idx[lowterm][2] += document_dictionary[term]

                        else:
                            if term in self.inverted_idx:
                                self.inverted_idx[term][0] += 1
                                self.inverted_idx[term][1][tweetID] = [max_tf, document_dictionary[term],
                                                                       num_unique_terms, doc_length]
                                self.inverted_idx[term][2] += document_dictionary[term]

                            else:  # if upper comes more than once
                                self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,
                                                                    num_unique_terms, doc_length)


                else:
                    """if term isn't a word, but hashtag, crucit or number"""
                    if term in self.inverted_idx:
                        self.inverted_idx[term][0] += 1
                        self.inverted_idx[term][1][tweetID] = [max_tf, document_dictionary[term], num_unique_terms,
                                                               doc_length]
                        self.inverted_idx[term][2] += document_dictionary[term]
                    else:  # if it comes more than once
                        self.adding_term_if_not_on_inverted(term, document_dictionary[term], tweetID, max_tf,
                                                            num_unique_terms, doc_length)

            except:
                print('problem with the following key {}'.format(term[0]))
        if self.is_using_global_method:
            # sending dict to update matrix dictionary
            new_dictionary = {x: val for x, val in document_dictionary.items() if
                              x.upper() in self.inverted_idx or x.lower() in self.inverted_idx}
            if len(new_dictionary) > 0:
                self.dets_for_matrix(new_dictionary)

    def adding_term_if_not_on_inverted(self, term, repAmount, tweetID, max_tf, numOfUniqueWords, doc_length):
        self.inverted_idx[term] = [1, {tweetID: [max_tf, repAmount, numOfUniqueWords, doc_length]}, repAmount, 0, '', 0]

    # run on all of the documents and insert to dict
    def insert_to_tweets_dict(self):
        for term in self.inverted_idx:
            tweetID_dict = self.inverted_idx[term][1]
            for tweetID, value in tweetID_dict.items():
                new_value = value.copy()
                new_value.append(self.inverted_idx[term][0])
                if tweetID in self.inverted_docs:
                    self.inverted_docs[tweetID][term] = new_value
                else:
                    self.inverted_docs[tweetID] = {term: new_value}

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
        with open(fn, 'rb') as f:
            return pickle.load(f)

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
        self.inverted_idx = dict(sorted(self.inverted_idx.items(), key=lambda item: item[0]))
        self.inverted_docs = dict(sorted(self.inverted_docs.items(), key=lambda item: item[0]))
        pickle_save.insert(0, self.inverted_idx)
        pickle_save.insert(1, self.inverted_docs)

        with open(fn, 'wb') as f:
            pickle.dump(pickle_save, f, pickle.HIGHEST_PROTOCOL)
        f.close()

        # utils.save_obj(pickle_save, fn)

        self.inverted_idx.clear()
        self.inverted_docs.clear()

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term, inverted_idx):
        """
        Checks if a term exist in the dictionary.
        """
        return term in inverted_idx

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_doc_posting_list(self, terms):
        """
        Return the posting list from the index for a term.
        """
        posting = self.load_index(self.config.get_savedFileInverted())
        inverted_idx = posting[0]
        inverted_docs = posting[1]
        terms_posting = {}
        tweets_id = []
        for term in terms:
            if not self._is_term_exist(term.lower(), inverted_idx) and not self._is_term_exist(term.upper(),inverted_idx):
                continue
            if self._is_term_exist(term.lower(), inverted_idx):
                term_to_save = term.lower()
            elif self._is_term_exist(term.upper(), inverted_idx):
                term_to_save = term.upper()
            terms_posting[term_to_save] = inverted_idx[term_to_save]
            tweets_id.extend(list(terms_posting[term_to_save][1].keys()))
        docs_posting = self.get_doc_posting_list(tweets_id, inverted_docs)
        return terms_posting, docs_posting

    def get_doc_posting_list(self, tweets_id, inverted_docs):
        """
        Return the posting list from the index for a doc.
        """
        docs_posting = {}
        for id in tweets_id:
            docs_posting[id] = inverted_docs[id]
        return docs_posting

    def get_inverted_docs(self):
        inverted_docs = self.load_index(self.config.get_savedFileInverted())[1]
        return inverted_docs

    def get_number_of_documents(self):
        return self.number_of_documents

    # save for each { (w1,w2) : cij }
    def dets_for_matrix(self, term_dict):
        list_of_keys = list(term_dict.keys())
        for i in range(len(list_of_keys)):
            for j in range(i + 1):

                w1 = list_of_keys[i].lower()
                w2 = list_of_keys[j].lower()
                w1_inv = ''
                w2_inv = ''
                # current recurr of each term in this tweet
                fik = term_dict[list_of_keys[i]]
                fjk = term_dict[list_of_keys[j]]

                #calc Cij for this doc
                cij = fik * fjk

                if w1 in self.inverted_idx:
                    w1_inv = w1
                elif w1.upper() in self.inverted_idx:
                    w1_inv = w1.upper()
                if w2 in self.inverted_idx:
                    w2_inv = w2
                elif w2.upper() in self.inverted_idx:
                    w2_inv = w2.upper()
                # update inv' index with cii and cjj
                if w1_inv == w2_inv:
                    cii = fik * fik
                    self.inverted_idx[w1_inv][3] += cii
                    continue
                # saving all tuples of words as lower cases to dict
                key_to_check = (w1, w2)
                if w1 > w2:
                    key_to_check = (w2, w1)
                if key_to_check not in self.AssocMatrixDetails:
                    self.AssocMatrixDetails[key_to_check] = cij
                else:
                    self.AssocMatrixDetails[key_to_check] += cij

    def calc_Sij(self):
        dict = self.AssocMatrixDetails
        all_keys = list(dict.keys())
        for i in range(len(dict)):
            term1 = all_keys[i][0]
            term2 = all_keys[i][1]
            if term1 not in self.inverted_idx:
                term1 = term1.upper()
            if term2 not in self.inverted_idx:
                term2 = term2.upper()
            cii = self.inverted_idx[term1][3]
            cjj = self.inverted_idx[term2][3]
            cij = dict[all_keys[i]]
            if (cii + cjj - cij) > 0:
                sij = cij / (cii + cjj - cij)
                if sij > 0.8:
                    if self.inverted_idx[term1][5] < sij:
                        self.inverted_idx[term1][4] = term2
                        self.inverted_idx[term1][5] = sij
                    if self.inverted_idx[term2][5] < sij:
                        self.inverted_idx[term2][4] = term1
                        self.inverted_idx[term2][5] = sij

    # doing Searcher's logic before retrieving relevant docs
    def global_expansion(self, query_as_list):
        inverted_index = self.load_index(self.config.get_savedFileInverted())[0]
        # iterate and expand query if Sij > 0.5
        for i in range(len(query_as_list)):
            if query_as_list[i].upper() in inverted_index:
                if inverted_index[query_as_list[i].upper()][4] != '':
                    query_as_list.append(inverted_index[query_as_list[i].upper()][4])
            elif query_as_list[i].lower() in inverted_index:
                if inverted_index[query_as_list[i].lower()][4] != '':
                    query_as_list.append(inverted_index[query_as_list[i].lower()][4])
        return query_as_list

    def isGlobal(self):
        return self.is_using_global_method

    def setGlobal(self, bool):
        self.is_using_global_method = bool
