from ranker import Ranker
import utils


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
        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        relevant_docs_dict =
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs, self._indexer.get_number_of_documents())
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping term to document frequency and inv_index term's value.
        """
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
        inv_index = self._indexer.get_term_posting_list(query_as_list)
        for term in inv_index.keys():
            if term.upper() in term_dict:
                new_term = term.upper()
            elif term.lower() in term_dict:
                new_term = term.lower()
            relevant_docs[new_term] = (term_dict[new_term],inv_index[term])
        return relevant_docs