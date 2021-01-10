# DO NOT MODIFY CLASS NAME
import copy
import utils


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # {term : [NumOfDiffDocs, {tweetID : [max_tf, repAmount, numOfUniqueWords, doc_length]}, NumOfCurrInTweetInCorpus,Cij]}
        self.inverted_docs = {}  # {tweetID : {term : [inverted_idx[term][tweetID], NumOfDiffDocs]}}
        self.config = config
        self.EntityDict = {}
        self.AssocMatrixDetails = {}  # (w1,w2) = Cij
        self.number_of_documents = 0
        self.is_using_global_method = False
        self.is_using_WordNet_method = False
        self.is_using_SpellCorrection_method = False
        self.is_using_Thesaurus_method = False
        self.is_using_Word2Vec = False

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
                    self.inverted_idx[term] = [2, dict_to_add, occurInCorpus, 0]
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
                            self.inverted_idx[term] = [self.inverted_idx[upterm][0] + 1, dict_to_add,self.inverted_idx[upterm][2] + document_dictionary[term],self.inverted_idx[upterm][3]]
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
        self.inverted_idx[term] = [1, {tweetID: [max_tf, repAmount, numOfUniqueWords, doc_length]}, repAmount, 0]

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
    """Structure of file: file[0] = inverted index, file[1] = inverted docs, file[2] = assoc matrix"""
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        return utils.load_obj(fn)

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
        if self.isGlobal():
            pickle_save.insert(2, self.AssocMatrixDetails)

        utils.save_obj(pickle_save, fn)

        self.inverted_idx.clear()
        self.inverted_docs.clear()
        if self.isGlobal():
            self.AssocMatrixDetails.clear()

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term, inverted_idx):
        """
        Checks if a term exist in the dictionary.
        """
        return term in inverted_idx

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_doc_posting_list(self, terms, inverted_idx, inverted_docs):
        """
        Return the posting list from the index for a term.
        """
        terms_posting = {}
        tweets_id = []
        for term in terms:
            if not self._is_term_exist(term.lower(), inverted_idx) and not self._is_term_exist(term.upper(), inverted_idx):
                continue
            if self._is_term_exist(term.lower(), inverted_idx):
                term_to_save = term.lower()
            elif self._is_term_exist(term.upper(), inverted_idx):
                term_to_save = term.upper()
            # TODO: FOR INCREASING PRECISION - Remove tweet that their length lower than query length (or equal)
            # list_of_tweets = list(inverted_idx[term_to_save][1].keys())
            # for id in list_of_tweets:
            #     if inverted_idx[term_to_save][1][id][3] <= len(terms):
            #         inverted_idx[term_to_save][1].pop(id)
            # TODO: FOR INCREASING PRECISION - Remove tweet that their length lower than query length (or equal)
            terms_posting[term_to_save] = inverted_idx[term_to_save]
            tweets_id.extend(list(terms_posting[term_to_save][1].keys()))
        docs_posting = self.get_doc_posting_list(tweets_id, inverted_docs)

        terms_posting, docs_posting = self.delete_docs_shorter_query(docs_posting, terms, terms_posting)

        # if len(terms) > 2:
        #     terms_posting, docs_posting = self.delete_doc_2_term_query(docs_posting, terms, terms_posting)

        #deleting documents that have a word with a different context from the query
        # if self.is_using_Word2Vec:
        #     new_docs = copy.deepcopy(docs_posting)
        #     check_context = []
        #     check_context.extend(terms)
        #     for doc, tweets in docs_posting.items():
        #         for word in tweets:
        #             if word.lower() in self.model:
        #                 check_context.append(word.lower())
        #         check_context = list(set(check_context))
        #         dont_match = self.model.wv.doesnt_match(check_context)
        #         if dont_match.upper() in tweets or dont_match in tweets and dont_match.upper() not in terms and dont_match not in terms:
        #             del new_docs[doc]
        #
        #     new_terms = copy.deepcopy(terms_posting)
        #     for term, values in terms_posting.items():
        #         for doc in values[1]:
        #             if doc in new_docs:
        #                 del new_terms[term][1][doc]
        #
        #     return new_terms, new_docs

        return terms_posting, docs_posting

    # FOR INCREASING PRECISION - Remove tweet that that have less than two terms from the query
    def delete_doc_2_term_query(self, docs_posting, terms, terms_posting):
        finall_docs_posting = {}
        for tweet, term in docs_posting.items():
            count = 0
            for term1 in terms:
                if term1 in term:
                    if ' ' in term1 or term1[0] == '#':
                        continue
                    else:
                        count += 1
                if count == 2:
                    finall_docs_posting[tweet] = term
                    break

        finall_terms_posting = copy.deepcopy(terms_posting)

        for term, value in terms_posting.items():
            for doc, terms in value[1].items():
                if doc not in finall_docs_posting:
                    del finall_terms_posting[term][1][doc]

        return finall_terms_posting, finall_docs_posting

    #FOR INCREASING PRECISION - Remove tweet that their length lower than query length or equal
    def delete_docs_shorter_query(self, docs_posting, terms, terms_posting):
        finall_docs_posting = {}
        for tweet, term in docs_posting.items():
            if len(term) > len(terms):
                finall_docs_posting[tweet] = term

        finall_terms_posting = copy.deepcopy(terms_posting)

        for term, value in terms_posting.items():
            for doc, terms in value[1].items():
                if doc not in finall_docs_posting:
                    del finall_terms_posting[term][1][doc]

        return finall_terms_posting, finall_docs_posting

    def get_doc_posting_list(self, tweets_id, inverted_docs):
        """
        Return the posting list from the index for a doc.
        """
        docs_posting = {}
        for id in tweets_id:
            docs_posting[id] = inverted_docs[id]
        return docs_posting

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
        # TODO : CHANGED TO x TO REMOVE WORDS WITH LOW CURRENCES
        # list_to_remove_currences = set()
        # list_to_remove_from_matrix = set()
        # TODO : CHANGED TO x TO REMOVE WORDS WITH LOW CURRENCES
        all_keys = list(dict.keys())
        for i in range(len(dict)):
            term1 = all_keys[i][0]
            term2 = all_keys[i][1]
            if term1 not in self.inverted_idx:
                term1 = term1.upper()
            if term2 not in self.inverted_idx:
                term2 = term2.upper()
            #TODO : CHANGED TO 2 TO REMOVE WORDS WITH LOW CURRENCES
            # if self.inverted_idx[term1][2] < 5:
            #     list_to_remove_currences.add(term1)
            # if self.inverted_idx[term2][2] < 5:
            #     list_to_remove_currences.add(term2)
            #     list_to_remove_from_matrix.add(all_keys[i])
            # TODO : CHANGED TO 3 TO REMOVE WORDS WITH LOW CURRENCES
            cii = self.inverted_idx[term1][3]
            cjj = self.inverted_idx[term2][3]
            cij = dict[all_keys[i]]
            if (cii + cjj - cij) > 0:
                sij = cij / (cii + cjj - cij)
                if sij > 1:
                    print("DANIEL DINSHTEIN MOSHESH MOSHESITO")
                # update matrix
                self.AssocMatrixDetails[all_keys[i]] = sij
        # TODO : CHANGED TO x TO REMOVE WORDS WITH LOW CURRENCES
        # for term in list_to_remove_currences:
        #     self.inverted_idx.pop(term)
        # for key in list_to_remove_from_matrix:
        #     self.AssocMatrixDetails.pop(key)
        # TODO : CHANGED TO x TO REMOVE WORDS WITH LOW CURRENCES

    def check_words_score_WordNet_Thesaurus_with_global(self,query_as_list,list_of_syns,AssocMatrixDetails):
        list_to_rank = []
        for tuple in list_of_syns:
            key1_of_tuple = tuple[0].lower()
            key2_of_tuple = tuple[1].lower()
            if key1_of_tuple < key2_of_tuple:
                tuple_new = (key1_of_tuple,key2_of_tuple)
            else:
                tuple_new = (key2_of_tuple,key1_of_tuple)
            if tuple_new in AssocMatrixDetails:
                # structure of list = [(('a','b'),0.5),(('c','d'),0.5)]
                list_to_rank.append((tuple_new,AssocMatrixDetails[tuple_new]))
        list_to_rank.sort(key=lambda x: x[1], reverse=True)
        #only 2 best scores
        final_list=[]
        list_to_rank_final = [x[0] for x in list_to_rank]
        list_to_rank_final=list_to_rank_final[:2]
        for key in list_to_rank_final:
            if key[0] in query_as_list:
                final_list.append(key[1])
            else:
                final_list.append(key[0])
        return final_list

    # doing Searcher's logic before retrieving relevant docs
    def global_expansion(self, query_as_list, inverted_index, AssocMatrixDetails):
        list_expanded = []
        copy_of_query = query_as_list.copy()
        AssocMatrixDetails = dict(sorted(AssocMatrixDetails.items(), key=lambda item: item[1], reverse=True))
        for tuple_of_keys , Sij in AssocMatrixDetails.items():
            key1 = tuple_of_keys[0]
            key2 = tuple_of_keys[1]
            # if Sij is not high enough,
            # or finished expanding each word with one fit word,
            # or expanded too much -> stop expanding query
            if (len(list_expanded) >= 2) or Sij < 0.2 or len(copy_of_query) == 0:
                return list_expanded
            # or both of the keys are not inside the query,
            # or both of the keys are inside the query
            # -> not relevant enough to expand
            if (key1 not in copy_of_query and key2 not in copy_of_query) or (key1 in copy_of_query and key2 in copy_of_query):
                continue
            # one of the keys is inside the query, and has not been added yet
            elif key1 in copy_of_query and key2 not in list_expanded:
                if key2.lower() in inverted_index:
                    list_expanded.append(key2.lower())
                elif key2.upper() in inverted_index:
                    list_expanded.append(key2.upper())
                copy_of_query.remove(key1)
            elif key2 in copy_of_query and key1 not in list_expanded:
                if key1.lower() in inverted_index:
                    list_expanded.append(key1.lower())
                elif key1.upper() in inverted_index:
                    list_expanded.append(key1.upper())
                copy_of_query.remove(key2)

        return list_expanded

    def isGlobal(self):
        return self.is_using_global_method

    def setGlobal(self, bool):
        self.is_using_global_method = bool

    def isWordNet(self):
        return self.is_using_WordNet_method

    def setWordNet(self, bool):
        self.is_using_WordNet_method = bool

    def setSpellCorrection(self,bool):
        self.is_using_SpellCorrection_method = bool

    def isSpellCorrection(self):
        return self.is_using_SpellCorrection_method

    def isThesaurus(self):
        return self.is_using_Thesaurus_method

    def setThesaurus(self, bool):
        self.is_using_Thesaurus_method = bool

    def setWord2Vec(self, bool):
        self.is_using_Word2Vec = bool

    def isWord2Vec(self):
        return self.is_using_Word2Vec

    def get_files(self):
        return self.load_index(self.config.get_saveInvertedPath())