import nltk
# nltk.download('wordnet')
from ranker import Ranker
import utils
from nltk.corpus import wordnet
from spellchecker import SpellChecker


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
        query_as_list = self._parser.parse_sentence(query, None)
        relevant_docs, relevant_inverted_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_inverted_docs)
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
        inv_idx = self._indexer.returnInv_Index()
        if self._indexer.isGlobal():
            list_to_expand = self._indexer.global_expansion(query_as_list)
            query_as_list.extend(list_to_expand)
        if self._indexer.isWordNet():
            list_to_expand = self.WordNet_expansion(query_as_list,inv_idx)
            query_as_list.extend(list_to_expand)
        if self._indexer.isSpellCorrection():
            list_to_expand,list_to_remove_from_query = self.SpellCorrection_replacement(query_as_list,inv_idx)
            # intersection between copy of query to query itself
            query_as_list = [value for value in list_to_remove_from_query if value in query_as_list]
            query_as_list.extend(list_to_expand)


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
        inv_index, relevant_inverted_docs = self._indexer.get_term_doc_posting_list(query_as_list)
        for term in query_as_list:
            if term.upper() in inv_index:
                new_term = term.upper()
            elif term.lower() in inv_index:
                new_term = term.lower()
            else:
                continue
            relevant_docs[new_term] = (term_dict[term], inv_index[new_term])
        return relevant_docs, relevant_inverted_docs

    def WordNet_expansion(self, query_as_list,inv_idx):
        synonyms = []  # milim nirdafot
        for term in query_as_list:
            counter_for_adding = 0
            synslist = wordnet.synsets(term)
            for syns in synslist:  # for every mila nirdefet
                lemmas = set(syns._lemma_names)
                for l in lemmas:
                    if l not in query_as_list and counter_for_adding <= 2 and (l.lower() in inv_idx or l.upper() in inv_idx):
                        synonyms.append(l)
                        counter_for_adding += 1
        return synonyms

    def SpellCorrection_replacement(self, query_as_list,inv_idx):
        query = query_as_list.copy()
        spell = SpellChecker()
        res =[]
        corrected = spell.unknown(query_as_list).union(spell.known(query_as_list))
        if len(corrected) == 0:
            return corrected
        for term in corrected:
            correct = spell.correction(term)
            # query will help us check which terms got replaced by spell-correction
            if correct not in query and (correct.lower() in inv_idx or correct.upper() in inv_idx) and correct != term:
                res.append(correct)
                query.remove(term)
        return res,query

