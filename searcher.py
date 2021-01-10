import copy

import nltk
# nltk.download('wordnet')
# nltk.download('lin_thesaurus')
from ranker import Ranker
from nltk.corpus import wordnet
from spellchecker import SpellChecker
from nltk.corpus import lin_thesaurus as Thesaurus


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model
    # parameter allows you to pass in a precomputed model that is already in
    # memory for the searcher to use such as LSI, LDA, Word2vec models.
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        query_as_list = self._parser.parse_sentence(query)
        relevant_docs, relevant_inverted_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_inverted_docs)

        #word2vec ranking (model vectors)
        if self._indexer.isWord2Vec():
            ranked_doc_ids = Ranker.rank_relevant_docs_w2v(self._model, relevant_docs, relevant_inverted_docs)
        else:
            ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs, self._indexer.get_number_of_documents(),
                                                       relevant_inverted_docs)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping term to document frequency and inv_index term's value.
        """
        # if we are using global method - expanding the query using association matrix
        read_file = self._indexer.get_files()
        inv_idx = read_file[0]
        inv_docs = read_file[1]
        if self._indexer.isGlobal():
            AssocMatrix = read_file[2]

        # var to measure how much we expanded our query -> so we don't exaggerate
        how_much_expanded = 0
        if self._indexer.isGlobal():
            list_to_expand = self._indexer.global_expansion(query_as_list,inv_idx,AssocMatrix)
            query_as_list.extend(list_to_expand)
            how_much_expanded += len(list_to_expand)
        if self._indexer.isWordNet() and how_much_expanded < 2:
            list_to_expand = self.WordNet_expansion(query_as_list, inv_idx,AssocMatrix)
            query_as_list.extend(list_to_expand)
        if self._indexer.isSpellCorrection():
            list_to_expand,list_to_remove_from_query = self.SpellCorrection_replacement(query_as_list,inv_idx)
            # intersection between copy of query to query itself
            query_as_list = [value for value in list_to_remove_from_query if value in query_as_list]
            query_as_list.extend(list_to_expand)
        if self._indexer.isThesaurus() and how_much_expanded < 2 or (self._indexer.isWordNet() and how_much_expanded < 3):
            list_to_expand = self.Thesaurus_expansion(query_as_list, inv_idx,AssocMatrix)
            query_as_list.extend(list_to_expand)
        # if self._indexer.isWord2Vec():
        #     query_as_list = self.word2vec_expansion(query_as_list, inv_idx)

        relevant_docs = {}
        query_as_list = sorted(query_as_list)
        term_dict = {}

        # same as dict created in func parse_Doc
        for term in query_as_list:
            if term not in term_dict:
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        # get partially inv_index from file on disk
        inv_index, relevant_inverted_docs = self._indexer.get_term_doc_posting_list(query_as_list, inv_idx, inv_docs)
        for term in query_as_list:
            if term.upper() in inv_index:
                new_term = term.upper()
            elif term.lower() in inv_index:
                new_term = term.lower()
            else:
                continue
            relevant_docs[new_term] = (term_dict[term], inv_index[new_term])
        return relevant_docs, relevant_inverted_docs

    def WordNet_expansion(self, query_as_list, inv_idx,AssocMatrix):
        synonyms = set() # milim nirdafot
        counter_for_adding_per_query = 0
        for term in query_as_list:
            counter_for_adding_per_term = 0
            synslist = wordnet.synsets(term)
            for syns in synslist:  # for every mila nirdefet
                lemmas = set(syns._lemma_names)
                for l in lemmas:
                    if (l.lower() not in query_as_list and l.upper() not in query_as_list) and counter_for_adding_per_term <= 1 and counter_for_adding_per_query <= 3 and (l.lower() in inv_idx or l.upper() in inv_idx):
                        # list will have combination of each lemma, and term it connected to
                        synonyms.add((term,l))
                        counter_for_adding_per_term += 1
                        counter_for_adding_per_query += 1
        if self._indexer.isGlobal():
            synonyms_from_global = self._indexer.check_words_score_WordNet_Thesaurus_with_global(query_as_list, synonyms,AssocMatrix)
        if len(synonyms_from_global) == 0:
            return list([x[1] for x in synonyms])
        else:
            return synonyms_from_global

    def Thesaurus_expansion(self, query_as_list, inv_idx,AssocMatrix):
        synonyms_to_add = set()  # milim nirdafot
        counter_for_adding_per_query = 0
        for term in query_as_list:
            counter_for_adding_per_term = 0
            syns = Thesaurus.scored_synonyms(term)
            for tuple in syns:
                if len(tuple[1]) > 0:
                    dict_items = tuple[1]
                    # tuples for each synonym with score for relevant to term : (synonym,[0,1])
                    dict_tuple_of_items = list(dict_items)
                    for key in dict_tuple_of_items:
                        # allow to expand by max one synonym per term in query, and max 5 synonyms per query
                        if (key[0].lower() in inv_idx or key[0].upper() in inv_idx) and (key[0].lower() and key[0].upper() not in query_as_list) and counter_for_adding_per_term <= 1 and counter_for_adding_per_query <= 3:
                            #structure of list = [(('a',0.5),'b')),(('c',0.75),'d'))]
                            synonyms_to_add.add((key[0],term,key[1]))
                            counter_for_adding_per_term += 1
                            counter_for_adding_per_query += 1
        synonyms_to_add = sorted(synonyms_to_add, key=lambda x: x[2])
        synonyms_to_add = list([(x[0],x[1]) for x in synonyms_to_add])

        if self._indexer.isGlobal():
            synonyms_from_global = self._indexer.check_words_score_WordNet_Thesaurus_with_global(query_as_list, synonyms_to_add,AssocMatrix)
        if len(synonyms_from_global) == 0:
            return list([x[0] for x in synonyms_to_add])[:3]
        else:
            return synonyms_from_global
        # now check and expand the query by words with highest score

        # return only 3 synonyms by score

    def SpellCorrection_replacement(self, query_as_list, inv_idx):
        query = query_as_list.copy()
        spell = SpellChecker()
        res =[]
        corrected = spell.unknown(query_as_list).union(spell.known(query_as_list))
        # have not found any correction to query
        if len(corrected) == 0:
            return corrected
        for term in corrected:
            correct = spell.correction(term)
            # query will help us check which terms got replaced by spell-correction
            if correct not in query and (correct.lower() in inv_idx or correct.upper() in inv_idx) and correct != term:
                res.append(correct)
                query.remove(term)
        return res, query

    def word2vec_contraction(self, query_as_list):
        list = []
        for term in query_as_list:
            if term.lower() in self._model:
                list.append(term.lower())
        if len(list) > 2:
            dont_match = self._model.wv.doesnt_match(list)
            if dont_match.upper() in query_as_list:
                query_as_list.remove(dont_match.upper())
                return dont_match.upper()
            else:
                query_as_list.remove(dont_match)
                return dont_match
        else:
            return None

    # We will add  word into the query - word most similar from the model that also appears in the Inverted Index
    def word2vec_expansion(self, query_as_list, inv_index):
        new_query_as_list = copy.deepcopy(query_as_list)
        for term in query_as_list:
            if term.lower() in self._model:
                most_similar = self._model.wv.most_similar(term.lower(), topn=1)
                for s in most_similar:
                    similar = s[0]
                    if similar.upper() in inv_index:
                        new_query_as_list.append(similar.upper())
                    elif similar.lower() in inv_index:
                        new_query_as_list.append(similar.lower())
                    else:
                        continue
        return new_query_as_list

    # We will replace a word in a query with a word most similar to it from the model that also appears in the Inverted Index
    def word2vec_replacement(self, query_as_list, inv_index):
        new_query_as_list = copy.deepcopy(query_as_list)
        for term in query_as_list:
            if term.lower() in self._model and (term.lower() not in inv_index or term.upper() not in inv_index):
                most_similar = self._model.wv.most_similar(term.lower(), topn=1)
                for s in most_similar:
                    similar = s[0]
                    if similar.upper() in inv_index:
                        new_query_as_list.append(similar)
                        if term in new_query_as_list:
                            new_query_as_list.remove(term)
                    elif similar.lower() in inv_index:
                        new_query_as_list.append(similar)
                        if term in new_query_as_list:
                            new_query_as_list.remove(term)
                    else:
                        continue
        return new_query_as_list



